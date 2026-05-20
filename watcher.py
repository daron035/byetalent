import os
import subprocess
import sys
import threading
import time

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


def load_env_manual(filepath=".env"):
    """
    Читает .env файл вручную и возвращает словарь переменных.
    Поддерживает базовый формат: KEY=VALUE, игнорирует комментарии.
    """
    env_vars = {}
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return env_vars

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith("#"):
                continue

            # Разделяем только по первому знаку равно
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Удаляем кавычки вокруг значения, если они есть (одинарные или двойные)
                if len(value) >= 2 and (
                    (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'"))
                ):
                    value = value[1:-1]

                env_vars[key] = value
    return env_vars


class RestartOnChangeHandler(PatternMatchingEventHandler):
    def __init__(self, script_path, debounce_seconds=0.5):
        super().__init__(
            # Следим за .py и .env
            patterns=["*.py", ".env"],
            ignore_patterns=["*/__pycache__/*", "*.pyc", "*/.git/*", "*/.idea/*"],
            ignore_directories=False,
        )
        self.script_path = script_path
        self.process = None
        self.debounce_seconds = debounce_seconds
        self._timer = None
        self._lock = threading.Lock()
        self._last_event_time = 0
        self._last_path = None
        self.start_process()

    def start_process(self):
        if self.process:
            # Убиваем старый процесс, если он есть
            try:
                self.process.terminate()  # Лучше terminate чем kill (дает шанс закрыться мягко)
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception:
                pass

        print(f"--- Starting {self.script_path} ---")

        # 1. Берем текущие системные переменные
        new_env = os.environ.copy()

        # 2. Читаем .env нашей функцией
        manual_env = load_env_manual(".env")

        # 3. Обновляем переменные (значения из .env перезапишут системные, если есть конфликты)
        new_env.update(manual_env)

        # Запускаем процесс с новым окружением
        self.process = subprocess.Popen([sys.executable, "-m", self.script_path], env=new_env)

    def _debounced_restart(self):
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce_seconds, self.start_process)
            self._timer.start()

    def on_modified(self, event):
        if event.is_directory:
            return

        filename = os.path.basename(event.src_path)
        # Реагируем на .py и .env
        if not (filename.endswith(".py") or filename == ".env"):
            return

        now = time.time()
        if event.src_path == self._last_path and (now - self._last_event_time) < self.debounce_seconds:
            return

        self._last_path = event.src_path
        self._last_event_time = now

        print(f"File changed: {filename}, restarting...")
        self._debounced_restart()


if __name__ == "__main__":
    script_module = "src.__main__"

    # Следим за текущей папкой (.), чтобы поймать изменение .env в корне
    watch_path = "."

    event_handler = RestartOnChangeHandler(script_module, debounce_seconds=1.0)
    observer = Observer()
    observer.schedule(event_handler, path=watch_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

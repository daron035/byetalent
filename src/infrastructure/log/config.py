from pathlib import Path

from msgspec import Struct


class LoggingConfig(Struct):
    render_json_logs: bool = False
    path: Path | None = None
    level: str = "DEBUG"

import os
import tomllib

import msgspec


DEFAULT_CONFIG_PATH = "./config/config.template.toml"


def read_toml(path: str) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_config[T](config_type: type[T], config_scope: str | None = None, path: str | None = None) -> tuple[T, str]:
    if path is None:
        path = os.getenv("CONFIG_PATH", DEFAULT_CONFIG_PATH)

    data = read_toml(path)

    if config_scope is not None:
        data = data[config_scope]

    config = msgspec.convert(data, type=config_type)

    return config, path

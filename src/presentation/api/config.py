from msgspec import Struct


class APIConfig(Struct):
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = __debug__

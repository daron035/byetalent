from msgspec import Struct, field

from src.infrastructure.log.config import LoggingConfig
from src.infrastructure.persistence.postgres.config import PostgresConfig
from src.presentation.api.config import APIConfig


class Config(Struct):
    api: APIConfig = field(default_factory=APIConfig)
    db: PostgresConfig = field(default_factory=PostgresConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

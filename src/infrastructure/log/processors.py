from collections.abc import Callable

import msgspec.json
import structlog


ProcessorType = Callable[
    [structlog.types.WrappedLogger, str, structlog.types.EventDict],
    str | bytes,
]


def serialize_to_json(data: object) -> str:
    return msgspec.json.encode(data).decode("utf-8")


def get_render_processor(
    render_json_logs: bool = False,
    serializer: Callable[..., str | bytes] = serialize_to_json,
    colors: bool = True,
) -> ProcessorType:
    if render_json_logs:
        return structlog.processors.JSONRenderer(serializer=serializer)
    return structlog.dev.ConsoleRenderer(colors=colors)

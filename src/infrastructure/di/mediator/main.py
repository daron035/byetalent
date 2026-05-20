import logging

from dishka import AsyncContainer
from memediator import Mediator, MediatorImpl
from memediator.ioc import DishkaIoc
from memediator.middlewares.logging import LoggingMiddleware

from src.domain.common.events import Event
from src.infrastructure.log.event_handler import EventLogger


async def build_mediator(container: AsyncContainer) -> Mediator:
    middlewares = (LoggingMiddleware(level=logging.DEBUG),)
    mediator = MediatorImpl(ioc=DishkaIoc(container), middlewares=middlewares)

    mediator.register_event_handler(Event, EventLogger)

    return mediator

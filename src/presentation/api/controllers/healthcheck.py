from fastapi import APIRouter

from src.infrastructure.di import container
from src.infrastructure.persistence.postgres.services.healthcheck import PgHealthCheck


healthcheck_router = APIRouter(
    tags=["general"],
)


@healthcheck_router.get("/ping")
async def ping() -> dict:
    async with container() as request_container:
        db = await request_container.get(PgHealthCheck)
        await db.check()
    return {"ok": True}

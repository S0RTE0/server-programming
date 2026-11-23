import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from app.settings.db import engine, ping
from models import Base
from routers import game_runs_router, items_router, players_router, run_items_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(players_router)
app.include_router(game_runs_router)
app.include_router(items_router)
app.include_router(run_items_router)


@app.get("/")
def index_root():
    return {"message": "Hello World!"}


@app.get("/healthcheck", status_code=status.HTTP_200_OK)
async def db_healthcheck():
    is_alive = await ping()
    if not is_alive:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )
    return {"status": "healthy", "database": "connected"}

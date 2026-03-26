import os
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI
from redis.asyncio import from_url

from src.api.routes import router
from src.api.repositories.prediction_repository import PredictionRepository
from src.api.services.prediction_service import PredictionService
from src.models.CatVDogModel import CatVDogModel


def read_setting(name: str) -> str:
    file_path = os.getenv(f"{name}_FILE")
    if not file_path:
        raise RuntimeError(f"Missing required setting file pointer: {name}_FILE")

    value = Path(file_path).read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError(f"Empty setting in file for: {name}")

    return value


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_host = read_setting("REDIS_HOST")
    redis_port = read_setting("REDIS_PORT")
    redis_db = read_setting("REDIS_DB")
    redis_username = read_setting("REDIS_USERNAME")
    redis_password = read_setting("REDIS_PASSWORD")

    model_version = os.getenv("MODEL_VERSION", "1.0.0")
    device = os.getenv("MODEL_DEVICE", "cpu")
    classifier_key = os.getenv("CLASSIFIER_KEY", "LOG_REG")

    redis_url = (
        f"redis://{quote(redis_username)}:{quote(redis_password)}"
        f"@{redis_host}:{redis_port}/{redis_db}"
    )

    redis = from_url(redis_url, decode_responses=True)
    await redis.ping()

    model_service = CatVDogModel(config_path="config.ini", show_log=True)
    model_service.set_device(device)
    model_service.load_classifier(classifier_key)

    repository = PredictionRepository(redis)

    prediction_service = PredictionService(
        ml_service=model_service,
        repository=repository,
        model_version=model_version,
        prediction_repository=repository,
    )

    app.state.redis = redis
    app.state.prediction_service = prediction_service

    yield

    await redis.aclose()


app = FastAPI(
    title="Dog vs Cat API",
    lifespan=lifespan,
)

app.include_router(router)
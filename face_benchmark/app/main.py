from pathlib import Path

import yaml

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.model import (
    create_model_router,
)
from app.api.verify import (
    create_verify_router,
)
from app.services.benchmark_service import (
    BenchmarkService,
)
from app.services.model_service import (
    ModelService,
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[1]
)

CONFIG_PATH = (
    BASE_DIR /
    "configs" /
    "benchmark.yaml"
)


with CONFIG_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    config = yaml.safe_load(
        file
    )


print("=" * 60)
print("Kinetic HR")
print("Face Recognition Benchmark")
print("=" * 60)


model_service = ModelService(
    config=config,
   
)


benchmark_service = BenchmarkService(
    results_root=str(
        BASE_DIR /
        config["benchmark"][
            "results_root"
        ]
    ),
)


app = FastAPI(
    title="Kinetic HR Face Benchmark"
)


app.include_router(
    create_model_router(
        model_service
    ),
    prefix="/api",
)


app.include_router(
    create_verify_router(
        model_service,
        benchmark_service,
    ),
    prefix="/api",
)


app.mount(
    "/",
    StaticFiles(
        directory=str(
            BASE_DIR / "web"
        ),
        html=True,
    ),
    name="web",
)
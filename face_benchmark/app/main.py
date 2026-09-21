from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.register import (
    create_register_router,
)

from app.api.verify import (
    create_verify_router,
)

from app.models.factory import (
    create_face_model,
)

from app.services.benchmark_service import (
    BenchmarkService,
)

from app.services.face_service import (
    FaceService,
)

from app.storage.embedding_store import (
    EmbeddingStore,
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

    config = yaml.safe_load(file)


print("=" * 60)
print("Kinetic HR")
print("Face Recognition Benchmark")
print("=" * 60)


face_model = create_face_model(
    config
)

face_model.load()


embedding_store = EmbeddingStore(
    root=str(
        BASE_DIR /
        config["storage"][
            "embedding_root"
        ]
    ),
    model_name=
        face_model.get_model_name(),
)


face_service = FaceService(
    model=face_model,
    store=embedding_store,
    threshold=
        config["recognition"][
            "threshold"
        ],
)


benchmark_service = BenchmarkService(
    results_root=str(
        BASE_DIR /
        config["benchmark"][
            "results_root"
        ]
    ),
    model_name=
        face_model.get_model_name(),
)


app = FastAPI(
    title="Kinetic HR Face Benchmark"
)


app.include_router(
    create_register_router(
        face_service
    ),
    prefix="/api",
)


app.include_router(
    create_verify_router(
        face_service,
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
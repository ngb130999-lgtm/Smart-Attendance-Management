from app.models.insightface_adapter import (
    InsightFaceAdapter,
)


def create_face_model(
    config: dict,
    model_name: str | None = None,
):
    if model_name is None:
        model_name = config["model"]["default"]

    models = config["models"]

    if model_name not in models:
        raise ValueError(
            f"Unsupported model: {model_name}"
        )

    if not models[model_name].get(
        "enabled",
        False,
    ):
        raise ValueError(
            f"Model is disabled: {model_name}"
        )

    providers = config["device"]["providers"]

    det_size = (
        config["detection"]["width"],
        config["detection"]["height"],
    )

    if model_name in {
        "buffalo_l",
        "antelopev2",
    }:
        return InsightFaceAdapter(
            model_name=model_name,
            providers=providers,
            det_size=det_size,
        )

    if model_name == "japanese_face_v1":
        from app.models.japanese_face_adapter import (
            JapaneseFaceAdapter,
        )

        return JapaneseFaceAdapter(
            config=config
        )

    raise ValueError(
        f"Unsupported model: {model_name}"
    )
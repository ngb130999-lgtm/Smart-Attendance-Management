from fastapi import APIRouter


def create_model_router(
    model_service,
):

    router = APIRouter()

    @router.get("/models")
    async def get_models():

        return {
            "default":
                model_service
                .get_default_model(),

            "models":
                model_service
                .get_available_models(),
        }

    return router
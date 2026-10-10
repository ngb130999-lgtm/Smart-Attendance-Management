from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.services.image_service import (
    decode_image,
)


def create_register_router(
    face_service,
):

    router = APIRouter()

    @router.post("/register")
    async def register(
        person_id: str = Form(...),
        images: list[UploadFile] = File(...),
    ):

        try:
            frames = []

            for upload in images:

                image_bytes = (
                    await upload.read()
                )

                frame = decode_image(
                    image_bytes
                )

                frames.append(frame)

            return face_service.register(
                person_id=person_id,
                images=frames,
            )

        except Exception as error:

            raise HTTPException(
                status_code=400,
                detail=str(error),
            )

    return router
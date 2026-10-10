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


def create_verify_router(
    model_service,
    benchmark_service,
):

    router = APIRouter()

    @router.post("/identify")
    async def identify(
        model_name: str = Form(...),
        actual_person: str = Form(...),
        condition: str = Form(...),
        image: UploadFile = File(...),
    ):

        try:

            image_bytes = (
                await image.read()
            )

            frame = decode_image(
                image_bytes
            )

            face_service = (
                model_service
                .get_face_service(
                    model_name
                )
            )

            result = (
                face_service.identify(
                    frame
                )
            )

            benchmark = (
                benchmark_service
                .save_identification(
                    result=result,
                    actual_person=
                        actual_person,
                    condition=condition,
                )
            )

            result["actual_person"] = (
                actual_person
            )

            result["outcome"] = (
                benchmark["outcome"]
            )

            result["correct"] = (
                benchmark["correct"]
            )

            benchmark_service.save_scores(
                result=result,
                actual_person=
                    actual_person,
                condition=condition,
                timestamp=
                    benchmark[
                        "timestamp"
                    ],
            )

            return result

        except Exception as error:

            raise HTTPException(
                status_code=400,
                detail=str(error),
            )

    return router
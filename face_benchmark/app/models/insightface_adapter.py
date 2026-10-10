import numpy as np
import onnxruntime as ort

from insightface.app import FaceAnalysis

from app.models.base import FaceModel


class InsightFaceAdapter(FaceModel):

    SUPPORTED_MODELS = {
        "buffalo_l",
        "antelopev2",
    }

    def __init__(
        self,
        model_name: str,
        providers: list[str],
        det_size: tuple[int, int],
    ):
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported InsightFace model: {model_name}"
            )

        self.model_name = model_name
        self.providers = providers
        self.det_size = det_size
        self.app = None

    def load(self) -> None:

        ort.preload_dlls(directory="")

        print(
            f"[INFO] Loading {self.model_name}..."
        )

        self.app = FaceAnalysis(
            name=self.model_name,
            providers=self.providers,
        )

        self.app.prepare(
            ctx_id=0,
            det_size=self.det_size,
        )

        print(
            f"[OK] {self.model_name} loaded."
        )

    def extract_embedding(
        self,
        image: np.ndarray,
    ) -> np.ndarray:

        if self.app is None:
            raise RuntimeError(
                "Face model is not loaded."
            )

        faces = self.app.get(image)

        if len(faces) == 0:
            raise ValueError(
                "顔を検出できませんでした。"
            )

        if len(faces) > 1:
            raise ValueError(
                "複数の顔が検出されました。"
            )

        embedding = (
            faces[0]
            .embedding
            .astype(np.float32)
        )

        norm = np.linalg.norm(embedding)

        if norm == 0:
            raise ValueError(
                "Invalid embedding."
            )

        return embedding / norm

    def get_model_name(self) -> str:
        return self.model_name
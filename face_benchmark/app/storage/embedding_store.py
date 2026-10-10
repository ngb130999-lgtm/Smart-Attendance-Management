from pathlib import Path
import re

import numpy as np


PERSON_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9_-]{1,64}$"
)


class EmbeddingStore:

    def __init__(
        self,
        root: str,
        model_name: str,
    ):
        self.model_name = model_name

        self.root = (
            Path(root) / model_name
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    @staticmethod
    def _validate_person_id(
        person_id: str,
    ) -> None:

        if not PERSON_ID_PATTERN.fullmatch(
            person_id
        ):
            raise ValueError(
                "Invalid person_id."
            )

    def save(
        self,
        person_id: str,
        embedding: np.ndarray,
    ) -> None:

        self._validate_person_id(
            person_id
        )

        path = (
            self.root /
            f"{person_id}.npy"
        )

        np.save(
            path,
            embedding.astype(np.float32),
        )

    def load(
        self,
        person_id: str,
    ) -> np.ndarray:

        self._validate_person_id(
            person_id
        )

        path = (
            self.root /
            f"{person_id}.npy"
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Person not registered: "
                f"{person_id}"
            )

        return np.load(path)

    def load_all(
        self,
    ) -> dict[str, np.ndarray]:

        embeddings = {}

        for path in self.root.glob("*.npy"):
            embeddings[path.stem] = np.load(
                path
            )

        return embeddings
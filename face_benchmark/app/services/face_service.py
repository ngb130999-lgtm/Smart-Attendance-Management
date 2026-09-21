import time

import numpy as np


class FaceService:

    def __init__(
        self,
        model,
        store,
        threshold: float,
    ):
        self.model = model
        self.store = store
        self.threshold = threshold

    @staticmethod
    def cosine_similarity(
        a: np.ndarray,
        b: np.ndarray,
    ) -> float:

        return float(
            np.dot(a, b)
        )

    def register(
        self,
        person_id: str,
        images: list[np.ndarray],
    ) -> dict:

        if not images:
            raise ValueError(
                "登録画像がありません。"
            )

        embeddings = []

        for image in images:

            embedding = (
                self.model
                .extract_embedding(image)
            )

            embeddings.append(
                embedding
            )

        reference = np.mean(
            embeddings,
            axis=0,
        )

        norm = np.linalg.norm(
            reference
        )

        if norm == 0:
            raise ValueError(
                "Invalid reference embedding."
            )

        reference = reference / norm

        self.store.save(
            person_id,
            reference,
        )

        return {
            "registered": True,
            "person_id": person_id,
            "model":
                self.model.get_model_name(),
            "capture_count":
                len(embeddings),
            "embedding_dimension":
                int(reference.shape[0]),
        }

    def identify(
        self,
        image: np.ndarray,
    ) -> dict:

        references = (
            self.store.load_all()
        )

        if not references:
            raise ValueError(
                "登録者が存在しません。"
            )

        start = time.perf_counter()

        query = (
            self.model
            .extract_embedding(image)
        )

        scores = {}

        for person_id, reference \
                in references.items():

            scores[person_id] = (
                self.cosine_similarity(
                    reference,
                    query,
                )
            )

        best_person = max(
            scores,
            key=scores.get,
        )

        best_score = scores[
            best_person
        ]

        matched = (
            best_score >= self.threshold
        )

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        return {
            "model":
                self.model.get_model_name(),

            "person_id":
                best_person
                if matched
                else None,

            "similarity":
                best_score,

            "threshold":
                self.threshold,

            "matched":
                matched,

            "latency_ms":
                elapsed_ms,

            "scores":
                scores,
        }
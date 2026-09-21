import csv
from datetime import datetime
from pathlib import Path


class BenchmarkService:

    RECOGNITION_HEADER = [
        "timestamp",
        "model",
        "actual_person",
        "predicted_person",
        "condition",
        "similarity",
        "threshold",
        "matched",
        "correct",
        "latency_ms",
    ]

    SCORE_HEADER = [
        "timestamp",
        "model",
        "actual_person",
        "reference_person",
        "condition",
        "similarity",
        "label",
    ]

    def __init__(
        self,
        results_root: str,
        model_name: str,
    ):

        self.directory = (
            Path(results_root) /
            model_name
        )

        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.recognition_path = (
            self.directory /
            "recognition_results.csv"
        )

        self.score_path = (
            self.directory /
            "score_results.csv"
        )

        self._create_if_missing(
            self.recognition_path,
            self.RECOGNITION_HEADER,
        )

        self._create_if_missing(
            self.score_path,
            self.SCORE_HEADER,
        )

    @staticmethod
    def _create_if_missing(
        path: Path,
        header: list[str],
    ):

        if path.exists():
            return

        with path.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=header,
            )

            writer.writeheader()

    def save_identification(
        self,
        result: dict,
        actual_person: str,
        condition: str,
    ) -> None:

        predicted = (
            result["person_id"]
        )

        correct = (
            predicted == actual_person
        )

        with self.recognition_path.open(
            "a",
            newline="",
            encoding="utf-8-sig",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=
                    self.RECOGNITION_HEADER,
            )

            writer.writerow({
                "timestamp":
                    datetime.now().isoformat(),

                "model":
                    result["model"],

                "actual_person":
                    actual_person,

                "predicted_person":
                    predicted or "UNKNOWN",

                "condition":
                    condition,

                "similarity":
                    result["similarity"],

                "threshold":
                    result["threshold"],

                "matched":
                    result["matched"],

                "correct":
                    correct,

                "latency_ms":
                    result["latency_ms"],
            })

    def save_scores(
        self,
        result: dict,
        actual_person: str,
        condition: str,
    ) -> None:

        timestamp = (
            datetime.now().isoformat()
        )

        with self.score_path.open(
            "a",
            newline="",
            encoding="utf-8-sig",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=self.SCORE_HEADER,
            )

            for (
                reference_person,
                similarity,
            ) in result["scores"].items():

                label = int(
                    actual_person
                    == reference_person
                )

                writer.writerow({
                    "timestamp":
                        timestamp,

                    "model":
                        result["model"],

                    "actual_person":
                        actual_person,

                    "reference_person":
                        reference_person,

                    "condition":
                        condition,

                    "similarity":
                        similarity,

                    "label":
                        label,
                })
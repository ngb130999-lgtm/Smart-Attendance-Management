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
        "outcome",
        "correct",
        "rank",
        "second_best_person",
        "second_best_similarity",
        "score_margin",
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
    ):
        self.results_root = Path(
            results_root
        )

    @staticmethod
    def determine_outcome(
        actual_person: str,
        predicted_person: str | None,
    ) -> str:

        if actual_person == "UNKNOWN":

            if predicted_person is None:
                return "CORRECT_REJECT"

            return "FALSE_ACCEPT"

        if predicted_person is None:
            return "FALSE_REJECT"

        if predicted_person == actual_person:
            return "CORRECT_ACCEPT"

        return "MISIDENTIFICATION"

    @staticmethod
    def _ensure_csv(
        path: Path,
        header: list[str],
    ) -> None:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

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
    ) -> dict:

        predicted = result[
            "person_id"
        ]

        outcome = (
            self.determine_outcome(
                actual_person,
                predicted,
            )
        )

        correct = outcome in {
            "CORRECT_ACCEPT",
            "CORRECT_REJECT",
        }

        model_name = result["model"]

        recognition_path = (
            self.results_root /
            model_name /
            "recognition" /
            (
                f"{actual_person}"
                "_recognition.csv"
            )
        )

        self._ensure_csv(
            recognition_path,
            self.RECOGNITION_HEADER,
        )

        timestamp = (
            datetime.now()
            .astimezone()
            .isoformat()
        )

        row = {
            "timestamp":
                timestamp,

            "model":
                model_name,

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

            "outcome":
                outcome,

            "correct":
                correct,

            "rank":
                result["rank"],

            "second_best_person":
                result[
                    "second_best_person"
                ] or "",

            "second_best_similarity":
                result[
                    "second_best_similarity"
                ],

            "score_margin":
                result["score_margin"],

            "latency_ms":
                result["latency_ms"],
        }

        with recognition_path.open(
            "a",
            newline="",
            encoding="utf-8-sig",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=
                    self.RECOGNITION_HEADER,
            )

            writer.writerow(row)

        return {
            "outcome": outcome,
            "correct": correct,
            "timestamp": timestamp,
        }

    def save_scores(
        self,
        result: dict,
        actual_person: str,
        condition: str,
        timestamp: str,
    ) -> None:

        model_name = result["model"]

        score_path = (
            self.results_root /
            model_name /
            "scores" /
            (
                f"{actual_person}"
                "_scores.csv"
            )
        )

        self._ensure_csv(
            score_path,
            self.SCORE_HEADER,
        )

        with score_path.open(
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
            ) in result[
                "scores"
            ].items():

                label = int(
                    actual_person
                    == reference_person
                )

                writer.writerow({
                    "timestamp":
                        timestamp,

                    "model":
                        model_name,

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
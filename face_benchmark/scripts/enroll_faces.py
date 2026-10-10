import argparse
import csv
import sys
from pathlib import Path

import cv2
import numpy as np
import yaml


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[1]
)

sys.path.insert(
    0,
    str(BASE_DIR),
)


from app.models.factory import (
    create_face_model,
)
from app.storage.embedding_store import (
    EmbeddingStore,
)


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
}


def load_config() -> dict:

    path = (
        BASE_DIR /
        "configs" /
        "benchmark.yaml"
    )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return yaml.safe_load(file)


def create_enrollment_csv(
    path: Path,
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "person_id",
            "model",
            "image_name",
            "pose",
            "face_detected",
            "face_count",
            "embedding_dimension",
            "embedding_norm",
            "used_for_template",
        ])


def append_enrollment_row(
    path: Path,
    row: list,
):

    with path.open(
        "a",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.writer(file)
        writer.writerow(row)


def infer_pose(
    image_name: str,
) -> str:

    name = image_name.lower()

    if "left" in name:
        return "slight_left"

    if "right" in name:
        return "slight_right"

    if "expression" in name:
        return "expression"

    return "front"


def enroll_person(
    config: dict,
    model,
    store: EmbeddingStore,
    model_name: str,
    person_id: str,
):

    person_directory = (
        BASE_DIR /
        config["storage"][
            "enrollment_root"
        ] /
        person_id
    )

    if not person_directory.exists():
        raise FileNotFoundError(
            f"Enrollment directory not found: "
            f"{person_directory}"
        )

    csv_path = (
        BASE_DIR /
        config["benchmark"][
            "results_root"
        ] /
        model_name /
        "enrollment" /
        f"{person_id}_enrollment.csv"
    )

    create_enrollment_csv(
        csv_path
    )

    embeddings = []

    image_paths = sorted(
        path
        for path
        in person_directory.iterdir()
        if path.suffix.lower()
        in IMAGE_EXTENSIONS
    )

    if not image_paths:
        raise ValueError(
            f"No enrollment images: "
            f"{person_id}"
        )

    for image_path in image_paths:

        image = cv2.imread(
            str(image_path)
        )

        if image is None:

            append_enrollment_row(
                csv_path,
                [
                    person_id,
                    model_name,
                    image_path.name,
                    infer_pose(
                        image_path.name
                    ),
                    False,
                    0,
                    "",
                    "",
                    False,
                ],
            )

            continue

        try:

            embedding = (
                model.extract_embedding(
                    image
                )
            )

            norm = float(
                np.linalg.norm(
                    embedding
                )
            )

            embeddings.append(
                embedding
            )

            append_enrollment_row(
                csv_path,
                [
                    person_id,
                    model_name,
                    image_path.name,
                    infer_pose(
                        image_path.name
                    ),
                    True,
                    1,
                    int(
                        embedding.shape[0]
                    ),
                    norm,
                    True,
                ],
            )

        except Exception as error:

            print(
                f"[WARN] "
                f"{image_path.name}: "
                f"{error}"
            )

            append_enrollment_row(
                csv_path,
                [
                    person_id,
                    model_name,
                    image_path.name,
                    infer_pose(
                        image_path.name
                    ),
                    False,
                    0,
                    "",
                    "",
                    False,
                ],
            )

    if not embeddings:
        raise ValueError(
            f"No valid face embeddings: "
            f"{person_id}"
        )

    template = np.mean(
        np.stack(
            embeddings,
            axis=0,
        ),
        axis=0,
    )

    norm = np.linalg.norm(
        template
    )

    if norm == 0:
        raise ValueError(
            "Template norm is zero."
        )

    template = (
        template / norm
    ).astype(np.float32)

    store.save(
        person_id,
        template,
    )

    print(
        f"[OK] {person_id}: "
        f"{len(embeddings)} images"
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        required=True,
    )

    parser.add_argument(
        "--person",
        default=None,
    )

    args = parser.parse_args()

    config = load_config()

    model = create_face_model(
        config=config,
        model_name=args.model,
    )

    model.load()

    store = EmbeddingStore(
        root=str(
            BASE_DIR /
            config["storage"][
                "embedding_root"
            ]
        ),
        model_name=args.model,
    )

    if args.person:

        persons = [
            args.person
        ]

    else:

        persons = config[
            "persons"
        ]

    for person_id in persons:

        enroll_person(
            config=config,
            model=model,
            store=store,
            model_name=args.model,
            person_id=person_id,
        )


if __name__ == "__main__":
    main()
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[1]
)


MODEL_NAME = "buffalo_l"


CSV_PATH = (
    BASE_DIR /
    "results" /
    MODEL_NAME /
    "score_results.csv"
)


def main():

    df = pd.read_csv(
        CSV_PATH
    )

    y_true = (
        df["label"]
        .astype(int)
        .to_numpy()
    )

    scores = (
        df["similarity"]
        .astype(float)
        .to_numpy()
    )

    auc = roc_auc_score(
        y_true,
        scores,
    )

    print("=" * 70)
    print(
        f"Model: {MODEL_NAME}"
    )
    print(
        f"ROC-AUC: {auc:.4f}"
    )
    print("=" * 70)

    thresholds = np.arange(
        0.20,
        0.81,
        0.01,
    )

    rows = []

    for threshold in thresholds:

        predicted = (
            scores >= threshold
        ).astype(int)

        tn, fp, fn, tp = (
            confusion_matrix(
                y_true,
                predicted,
                labels=[0, 1],
            )
            .ravel()
        )

        fmr = (
            fp / (fp + tn)
            if fp + tn > 0
            else 0.0
        )

        fnmr = (
            fn / (fn + tp)
            if fn + tp > 0
            else 0.0
        )

        precision = precision_score(
            y_true,
            predicted,
            zero_division=0,
        )

        recall = recall_score(
            y_true,
            predicted,
            zero_division=0,
        )

        f1 = f1_score(
            y_true,
            predicted,
            zero_division=0,
        )

        rows.append({
            "threshold":
                round(float(threshold), 2),

            "fmr":
                fmr,

            "fnmr":
                fnmr,

            "precision":
                precision,

            "recall":
                recall,

            "f1":
                f1,
        })

    result_df = pd.DataFrame(
        rows
    )

    output_path = (
        BASE_DIR /
        "results" /
        MODEL_NAME /
        "threshold_analysis.csv"
    )

    result_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"Saved: {output_path}"
    )


if __name__ == "__main__":
    main()
import cv2
import numpy as np


def decode_image(
    image_bytes: bytes,
) -> np.ndarray:

    array = np.frombuffer(
        image_bytes,
        dtype=np.uint8,
    )

    image = cv2.imdecode(
        array,
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise ValueError(
            "画像を読み込めませんでした。"
        )

    return image
from abc import ABC, abstractmethod

import numpy as np


class FaceModel(ABC):

    @abstractmethod
    def load(self) -> None:
        pass

    @abstractmethod
    def extract_embedding(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass
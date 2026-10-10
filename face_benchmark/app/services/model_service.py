from copy import deepcopy

from app.models.factory import (
    create_face_model,
)


class ModelService:

    def __init__(
        self,
        config: dict,
    ):
        self.config = config
        self._models = {}


    def get_available_models(
        self,
    ) -> list[dict]:

        models = []

        for (
            model_name,
            model_config,
        ) in self.config[
            "models"
        ].items():

            models.append({
                "name":
                    model_name,

                "enabled":
                    bool(
                        model_config.get(
                            "enabled",
                            False,
                        )
                    ),
            })

        return models


    def get_default_model(
        self,
    ) -> str:

        return self.config[
            "default_model"
        ]


    def get_model(
        self,
        model_name: str,
    ):

        models_config = self.config[
            "models"
        ]


        if (
            model_name
            not in models_config
        ):

            raise ValueError(
                f"Unknown model: {model_name}"
            )


        model_config = (
            models_config[
                model_name
            ]
        )


        if not model_config.get(
            "enabled",
            False,
        ):

            raise ValueError(
                f"Model is disabled: {model_name}"
            )


        if (
            model_name
            in self._models
        ):

            return self._models[
                model_name
            ]


        model_runtime_config = (
            deepcopy(
                self.config
            )
        )


        model_runtime_config[
            "model"
        ] = {
            "name":
                model_name
        }


        model = (
            create_face_model(
                model_runtime_config
            )
        )


        model.load()


        self._models[
            model_name
        ] = model


        return model
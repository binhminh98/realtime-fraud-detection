"""
Module to specify backend logic for the services for fraud detection ML models.
"""

import os
from pathlib import Path

import mlflow
from general_utils.logging import get_logger

file_logger = get_logger(
    "file_" + __name__,
    write_to_file=True,
    log_filepath=Path(r"logs/backend/inference_endpoints.log"),
)

stream_logger = get_logger(
    "stream_" + __name__,
)

mlflow_client = mlflow.MlflowClient(os.getenv("MLFLOW_URI"))
mlflow.set_tracking_uri(os.getenv("MLFLOW_URI"))


def get_champion_model():
    all_models = mlflow_client.search_model_versions()
    all_model_names = set([model.name for model in all_models])

    version = None
    model_name = None

    for model_name in all_model_names:
        try:
            version = mlflow_client.get_model_version_by_alias(
                name=model_name, alias="champion"
            )

            stream_logger.info(
                f"Champion found: model={model_name}, version={int(version.version)}"
            )

            break
        except Exception as e:
            file_logger.error(f"Error when getting champion model: {str(e)}")
            continue

    if version:
        model_uri = f"models:/{model_name}/{version.version}"
        loaded_model = mlflow.pyfunc.load_model(model_uri)

    else:
        loaded_model = None

    return loaded_model


champion_model = get_champion_model()


class InferenceUtils:

    @staticmethod
    def inference(item):
        item.update({"is_fraud": int(champion_model.predict(item)[0])})
        return item

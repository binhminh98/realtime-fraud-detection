"""
Module to specify backend logic for the services for fraud detection ML models.
"""

import logging
import os

import mlflow

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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

            logger.info(
                f"Champion found: model={model_name}, version={int(version.version)}"
            )

            break
        except Exception:
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

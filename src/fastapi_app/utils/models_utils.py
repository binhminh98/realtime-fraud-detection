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


class ModelUtils:

    @staticmethod
    def get_model_names():
        all_models = mlflow_client.search_model_versions()
        return list(set([model.name for model in all_models]))

    @staticmethod
    def get_champion_model_info():
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
            positive_precision = mlflow_client.get_metric_history(
                run_id=version.run_id, key="positive_precision"
            )[0].value

            positive_recall = mlflow_client.get_metric_history(
                run_id=version.run_id, key="positive_recall"
            )[0].value

            positive_f1 = mlflow_client.get_metric_history(
                run_id=version.run_id, key="positive_f1"
            )[0].value

            macro_precision = mlflow_client.get_metric_history(
                run_id=version.run_id, key="macro_precision"
            )[0].value

            macro_recall = mlflow_client.get_metric_history(
                run_id=version.run_id, key="macro_recall"
            )[0].value

            macro_f1 = mlflow_client.get_metric_history(
                run_id=version.run_id, key="macro_f1"
            )[0].value

            model_metrics = {
                "positive_precision": positive_precision,
                "positive_recall": positive_recall,
                "positive_f1": positive_f1,
                "macro_precision": macro_precision,
                "macro_recall": macro_recall,
                "macro_f1": macro_f1,
            }

            model_info = {
                "model_name": model_name,
                "model_version": int(version.version),
                "model_metrics": model_metrics,
            }

        else:
            model_info = None

        return model_info

    @staticmethod
    def get_model_info_by_name(model_name: str):
        try:
            registered_model = mlflow_client.get_registered_model(model_name)

            if registered_model:
                run_id = registered_model.latest_versions[0].run_id

                positive_precision = mlflow_client.get_metric_history(
                    run_id=run_id,
                    key="positive_precision",
                )[0].value

                positive_recall = mlflow_client.get_metric_history(
                    run_id=run_id, key="positive_recall"
                )[0].value

                positive_f1 = mlflow_client.get_metric_history(
                    run_id=run_id, key="positive_f1"
                )[0].value

                macro_precision = mlflow_client.get_metric_history(
                    run_id=run_id, key="macro_precision"
                )[0].value

                macro_recall = mlflow_client.get_metric_history(
                    run_id=run_id, key="macro_recall"
                )[0].value

                macro_f1 = mlflow_client.get_metric_history(
                    run_id=run_id, key="macro_f1"
                )[0].value

                model_metrics = {
                    "positive_precision": positive_precision,
                    "positive_recall": positive_recall,
                    "positive_f1": positive_f1,
                    "macro_precision": macro_precision,
                    "macro_recall": macro_recall,
                    "macro_f1": macro_f1,
                }

                model_info = {
                    "model_name": model_name,
                    "model_version": int(
                        registered_model.latest_versions[0].version
                    ),
                    "model_metrics": model_metrics,
                }
                print(model_info)

            else:
                model_info = None

            return model_info

        except Exception as e:
            return None

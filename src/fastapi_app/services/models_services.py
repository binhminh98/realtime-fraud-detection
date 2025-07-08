"""
Module to specify services for the endpoints for fraud detection ML models.
"""

from utils.models_utils import ModelUtils


class ModelServices:

    @staticmethod
    def get_model_names():
        return ModelUtils.get_model_names()

    @staticmethod
    def get_champion_model_info():
        return ModelUtils.get_champion_model_info()

    @staticmethod
    def get_model_info_by_name(model_name: str):
        return ModelUtils.get_model_info_by_name(model_name)

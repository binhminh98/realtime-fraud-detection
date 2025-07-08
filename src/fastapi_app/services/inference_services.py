"""
Module to specify services for the endpoints for fraud detection ML models.
"""

from utils.inference_utils import InferenceUtils


class InferenceServices:

    @staticmethod
    def inference(item):
        return InferenceUtils.inference(item)

"""
Module to specify services for the endpoints for data producers.
"""

from utils.producer_utils import ProducerUtil


class ProducerService:

    @staticmethod
    def get_producers():
        return ProducerUtil.get_producers()

    @staticmethod
    def produce_transactions(num_messages: int):
        return ProducerUtil.produce_transactions(num_messages)

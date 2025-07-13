"""
Module to specify backend logic for the services for data producers.
"""

from pathlib import Path

from data_utils.data_producers import TransactionProducer
from general_utils.logging import get_logger

file_logger = get_logger(
    "file_" + __name__,
    write_to_file=True,
    log_filepath=Path(r"logs/backend/producer_endpoints.log"),
)

stream_logger = get_logger(
    "stream_" + __name__,
)

transaction_producer = TransactionProducer()


class ProducerUtil:

    @staticmethod
    def get_producers() -> list | None:
        return [TransactionProducer.__name__]

    @staticmethod
    def produce_transactions(num_messages: int):
        transaction_producer.produce(num_messages)

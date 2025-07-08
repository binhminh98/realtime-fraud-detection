"""
Module to produce synthetic transaction data for a Kafka topic.
"""

import json
import pickle
import random
from abc import ABC, abstractmethod
from math import ceil
from time import sleep

import pandas as pd
from faker import Faker

from src.db_connectors.kafka.producer import KafkaProducer
from src.db_connectors.minio.minio_client import MinioClient


class DataProducer(ABC):
    """
    Abstract base class for data producers.
    """

    def __init__(self):
        self.faker = Faker()

    @abstractmethod
    def _generate_synthetic_data(self, num_messages) -> pd.DataFrame:
        """Generate a synthetic data point."""
        pass

    @abstractmethod
    def produce(self, num_messages: int):
        """
        Produce messages to a Kafka topic.
        """
        pass


class TransactionProducer(DataProducer):
    """
    Kafka producer for generating synthetic transaction data.
    """

    def __init__(self):
        super().__init__()
        self.producer = KafkaProducer()
        self.minio_client = MinioClient()
        self.topic = "transactions"
        self.real_fraud_data = self._get_real_fraud_data()
        self.fraud_transaction_synthesizer = self._get_synthesizer()

    def _get_synthesizer(self):

        """
        Load the synthesizers from Minio.
        """
        bucket_name = "synthesizers"
        file_name = "test_fraud_synthesizer_v4.pkl"

        cached_model = self.minio_client.get_file_buffer_as_bytes(
            bucket_name, file_name
        )

        if cached_model:
            synthesizer = pickle.load(cached_model)
        else:
            synthesizer = None

        return synthesizer

    def _get_real_fraud_data(self):
        """
        Get real fraud data from validation and test set
        """
        bucket_name = "creditcardfraud"
        file_name = "real_fraud_data.pkl"

        cached_data = self.minio_client.get_file_buffer_as_bytes(
            bucket_name, file_name
        )

        if cached_data:
            cached_data = pickle.load(cached_data)
        else:
            cached_data = None

        return cached_data

    # ### TODO: Move this method to the models classes for model training.
    # def _get_training_data(self):
    #     """
    #     Load training data from a Minio file.
    #     """
    #     bucket_name = "creditcardfraud"
    #     file_name = "creditcard.pkl"

    #     cached_data = self.minio_client.get_file_buffer_as_bytes(
    #         bucket_name, file_name
    #     )

    #     if cached_data:
    #         cached_data = pd.read_pickle(cached_data)
    #     else:
    #         cached_data = None

    #     return cached_data

    def _generate_synthetic_data(self, num_messages) -> pd.DataFrame:
        """Generate a synthetic transactions with 1-2% fraud rate."""
        # Get real fraud data from validation and test set.
        real_normal_data = self.real_fraud_data[
            self.real_fraud_data["Class"] == 0
        ]

        real_fraud_data = self.real_fraud_data[
            self.real_fraud_data["Class"] == 1
        ]

        # Sample synthetic transactions (0.1-0.2% fraud)
        fraud_percentage = random.uniform(0.001, 0.002)
        synthetic_fraud_percentage = 0.6
        real_fraud_percentage = 0.4

        num_fraud_messages = int(num_messages * fraud_percentage)

        num_synthetic_fraud_messages = ceil(
            num_fraud_messages * synthetic_fraud_percentage
        )

        num_real_fraud_messages = ceil(
            num_fraud_messages * real_fraud_percentage
        )

        num_normal_messages = num_messages - num_fraud_messages

        transactions = self.fraud_transaction_synthesizer.sample(
            num_synthetic_fraud_messages
        ).sample(num_synthetic_fraud_messages)

        transactions["Class"] = 1

        transactions = pd.concat(
            [
                real_normal_data.sample(
                    num_normal_messages,
                    replace=(num_normal_messages > len(real_normal_data)),
                ),
                transactions,
                real_fraud_data.sample(
                    num_real_fraud_messages,
                    replace=(num_real_fraud_messages > len(real_fraud_data)),
                ),
            ],
            ignore_index=True,
        )

        # Make fake id
        transactions["id"] = [
            self.faker.uuid4() for _ in range(len(transactions))
        ]

        return transactions.sample(frac=1)  # Shuffle so that fraud is random

    def produce(self, num_messages: int):
        """
        Produce messages to the specified Kafka topic.
        """
        transactions = self._generate_synthetic_data(num_messages).sample(
            frac=1
        )

        for i, transaction in transactions.iterrows():
            self.producer.produce(
                self.topic,
                key=transaction["id"],
                value=json.dumps(transaction.to_dict()),
            )

            # sleep(0.1)  # Simulate a delay between messages

if __name__ == "__main__":
    transaction_producer = TransactionProducer()
    transaction_producer.produce(num_messages=100000)

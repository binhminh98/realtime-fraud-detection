"""
Module to produce synthetic transaction data for a Kafka topic.
"""

import datetime
import json
import pickle
import random
from abc import ABC, abstractmethod
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
        self.training_data = self._get_training_data()
        self.fraud_transaction_synthesizer = self._get_synthesizer()
        self.normal_transaction_synthesizer = self._get_synthesizer(
            is_fraud=False
        )

    def _get_synthesizer(self, is_fraud: bool = True):
        """
        Load the synthesizers from Minio.
        """
        bucket_name = "synthesizers"
        file_name = (
            "fraud_synthesizer.pkl" if is_fraud else "normal_synthesizer.pkl"
        )

        cached_model = self.minio_client.get_file_buffer_as_bytes(
            bucket_name, file_name
        )

        if cached_model:
            synthesizer = pickle.load(cached_model)
        else:
            synthesizer = None

        return synthesizer

    ### TODO: Move this method to the models classes for model training.
    def _get_training_data(self):
        """
        Load training data from a Minio file.
        """
        bucket_name = "creditcardfraud"
        file_name = "creditcard.csv"

        return self.minio_client.get_csv_data(bucket_name, file_name)

    def _generate_synthetic_data(self, num_messages) -> pd.DataFrame:
        """Generate a synthetic transactions with 1-2% fraud rate."""

        # Sample synthetic transactions (0.1-0.2% fraud)
        fraud_percentage = random.uniform(0.001, 0.002)
        num_fraud_messages = int(num_messages * fraud_percentage)
        num_normal_messages = num_messages - num_fraud_messages

        # Synthesizer always make multiply of 128 samples, so we sample twice to get the desired number of messages
        normal_transactions = self.normal_transaction_synthesizer.sample(
            num_normal_messages
        )
        normal_transactions = normal_transactions.sample(num_normal_messages)
        normal_transactions["Class"] = 0

        fraud_transactions = self.fraud_transaction_synthesizer.sample(
            num_fraud_messages
        ).sample(num_fraud_messages)
        fraud_transactions = fraud_transactions.sample(num_fraud_messages)
        fraud_transactions["Class"] = 1

        transactions = pd.concat(
            [normal_transactions, fraud_transactions], ignore_index=True
        )

        # Make fake id
        transactions["id"] = [
            self.faker.uuid4() for _ in range(len(transactions))
        ]

        return transactions

    def produce(self, num_messages: int):
        """
        Produce messages to the specified Kafka topic.
        """
        transactions = self._generate_synthetic_data(num_messages)

        for i, transaction in transactions.iterrows():
            self.producer.produce(
                self.topic,
                key=transaction["id"],
                value=json.dumps(transaction.to_dict()),
            )

            # sleep(0.01)  # Simulate a delay between messages


if __name__ == "__main__":
    transaction_producer = TransactionProducer()
    transaction_producer.produce(num_messages=100000)

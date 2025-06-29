"""
Python module for generating synthetic data.
"""

import datetime
from abc import ABC, abstractmethod

from faker import Faker


class DataGenerator(ABC):
    def __init__(self):
        self.faker = Faker()

    @abstractmethod
    def generate_synthetic_data(self):
        """Generate a synthetic transaction message."""
        pass


class TransactionGenerator(DataGenerator):
    def __init__(self):
        """
        Initialize the TransactionGenerator with a Kafka topic.
        """
        super().__init__()

    def generate_synthetic_data(self):
        """Generate a synthetic transaction message."""

        transaction_id = self.faker.uuid4()
        amount = self.faker.random_number(
            digits=5, fix_len=True
        )  # Random amount between 10000 and 99999
        currency = "GBP"
        timestamp = datetime.datetime.now().isoformat()

        return {
            "id": transaction_id,
            "amount": amount,
            "currency": currency,
            "timestamp": timestamp,
        }

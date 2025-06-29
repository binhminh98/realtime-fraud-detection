"""
Module to produce synthetic transaction data for a Kafka topic.
"""

"""
Main entry point for the Realtime Fraud Detection application.
This module initializes the Kafka producer and consumer, and starts the data
generation process.
"""

import json

from src.data_utils.data_generators import TransactionGenerator
from src.db_connectors.kafka.producer import TransactionProducer


def main():
    """
    Main function to run the Realtime Fraud Detection application.
    It initializes the Kafka producer, generates synthetic transaction data,
    and stream it.
    """
    producer = TransactionProducer()
    transaction_generator = TransactionGenerator()

    topic = "transactions"

    for _ in range(5000):
        transaction = transaction_generator.generate_synthetic_data()

        producer.produce(
            topic, key=transaction["id"], value=json.dumps(transaction)
        )


if __name__ == "__main__":
    main()

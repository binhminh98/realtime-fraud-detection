""" "
Kafka producer.
"""

import os
from pathlib import Path

from confluent_kafka import Producer
from dotenv import load_dotenv
from general_utils.logging import get_logger

file_logger = get_logger(
    "file_" + __name__,
    write_to_file=True,
    log_filepath=Path(r"logs/kafka/kafka_producer.log"),
)

stream_logger = get_logger(
    "stream_" + __name__,
)

load_dotenv(override=True)


class KafkaProducer:
    def __init__(self):
        self.config = self._load_config()
        self.producer = self._create_producer()

    def _create_producer(self):
        """Create a Kafka producer with the loaded configuration."""
        return Producer(self.config)

    def _load_config(self):
        """Load Kafka configuration from environment variables or a config file."""

        return {
            "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        }

    def produce(self, topic, key, value):
        """Produce a message to the specified Kafka topic."""

        self.producer.produce(
            topic, key=key, value=value, callback=self._delivery_callback
        )

        self.producer.poll(1)
        self.producer.flush()

    @staticmethod
    def _delivery_callback(err, msg):
        if err:
            file_logger.error(f"ERROR: Message failed delivery: str{err}")
        else:
            stream_logger.info(
                f"Produced event to topic {msg.topic()}: key = {msg.key().decode('utf-8')} value = {msg.value().decode('utf-8')}"
            )


if __name__ == "__main__":
    import json

    producer = KafkaProducer()

    topic = "transactions"
    key = "transaction_id"
    value = {
        "id": "test",
        "amount": 100,
        "currency": "USD",
        "timestamp": "2023-10-01T12:00:00Z",
    }

    producer.produce(topic, key, json.dumps(value))

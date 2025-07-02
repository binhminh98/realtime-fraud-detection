"""
Kafka consumer.
"""

import os
from pathlib import Path

from confluent_kafka import Consumer
from dotenv import load_dotenv

from src.general_utils.logging import get_logger

file_logger = get_logger(
    "file_" + __name__,
    write_to_file=True,
    log_filepath=Path(r"logs/kafka/kafka_consumer.log"),
)

stream_logger = get_logger(
    "stream_" + __name__,
)


class KafkaConsumer:
    def __init__(self):
        self.config = self._load_config()
        self.consumer = self._create_consumer()

    def subscribe(self, topics):
        """Subscribe to the specified Kafka topics."""
        if isinstance(topics, str):
            topics = [topics]
        self.consumer.subscribe(topics)

    def _load_config(self):
        """Load Kafka configuration from environment variables or a config file."""
        load_dotenv(override=True)

        return {
            "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
            "group.id": "ml_transaction_consumer",
            "auto.offset.reset": "earliest",  # Start reading from the earliest message
        }

    def _create_consumer(self):
        """Create a Kafka consumer with the loaded configuration."""
        return Consumer(self.config)

    def consume(self):
        """Consume messages from the Kafka topic."""
        try:
            while True:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    file_logger.error(f"Error: {msg.error()}")
                    continue

                stream_logger.info(
                    f"Consumed message: {msg.value().decode('utf-8')} from topic {msg.topic()}"
                )
        finally:
            self.close()

    def close(self):
        """Close the consumer connection."""
        self.consumer.close()


if __name__ == "__main__":
    consumer = KafkaConsumer()
    topics = ["transactions"]
    consumer.subscribe(topics)
    consumer.consume()

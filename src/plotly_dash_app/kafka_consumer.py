import json
import threading
import time
from collections import deque
from datetime import datetime

import pandas as pd
import requests
from confluent_kafka import Consumer


class KafkaMessageCollector:

    def __init__(self, kafka_config, topic, fastapi_url):
        self.consumer = Consumer(kafka_config)
        self.consumer.subscribe([topic])
        self.prediction_history = []
        self.transaction_ground_truth = []
        self.inference_latencies = []
        self.fastapi_url = fastapi_url

        # Deque to hold recent messages
        self.buffer = deque(maxlen=30000)
        self.running = True
        self.thread = threading.Thread(target=self._consume_loop, daemon=True)
        self.thread.start()

    def _consume_loop(self):
        while self.running:
            message = self.consumer.poll(1.0)

            if message is None or message.error():
                continue

            try:
                message = json.loads(message.value().decode("utf-8"))

                start = time.time()

                inference_result = requests.post(
                    f"{self.fastapi_url}/inference/inference",
                    json=message,
                    timeout=2.0,
                ).json()

                end = time.time()

                timestamp = pd.to_datetime(
                    message.get("timestamp", datetime.utcnow())
                )

                self.inference_latencies.append(
                    {"timestamp": timestamp, "latency": end - start}
                )

                self.buffer.append(
                    {
                        "timestamp": timestamp,
                        "class": inference_result["Class"],
                        "is_fraud": inference_result["is_fraud"],
                    }
                )

                self.prediction_history.append(inference_result["is_fraud"])
                self.transaction_ground_truth.append(inference_result["Class"])

            except Exception as e:
                print(f"Error processing message: {e}")

    def get_transactions_in_buffer(self):
        return pd.DataFrame(self.buffer)

    def get_prediction_counts(self):
        predictions = pd.Series(self.prediction_history)

        if not predictions.empty:
            counts = {
                "message_type": ["normal", "fraud"],
                "counts": [(predictions == 0).sum(), (predictions == 1).sum()],
            }
        else:
            counts = None

        return pd.DataFrame(counts)

    def get_ground_truth_counts(self):
        ground_truths = pd.Series(self.transaction_ground_truth)

        if not ground_truths.empty:
            counts = {
                "message_type": ["normal", "fraud"],
                "counts": [
                    (ground_truths == 0).sum(),
                    (ground_truths == 1).sum(),
                ],
            }
        else:
            counts = None

        return pd.DataFrame(counts)

    def get_prediction_results(self):
        return self.prediction_history, self.transaction_ground_truth

    def get_average_latency(self):
        all_latency = [
            latency["latency"] for latency in self.inference_latencies
        ]

        return (
            sum(all_latency) / len(self.prediction_history)
            if self.prediction_history
            else 0
        )

    def get_inference_latencies(self):
        return pd.DataFrame(self.inference_latencies)

    def stop(self):
        self.running = False
        self.consumer.close()

"""
Kafka Historical User Event Consumer (Event Sourcing)
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import json
import os
from typing import Optional

from kafka import KafkaConsumer

from logger import Logger
from handlers.handler_registry import HandlerRegistry


class UserEventHistoryConsumer:
    """Reads all historical events from a Kafka topic."""

    def __init__(
            self,
            bootstrap_servers: str,
            topic: str,
            group_id: str,
            registry: HandlerRegistry
    ):
        self.topic = topic
        self.group_id = group_id
        self.registry = registry

        self.consumer: Optional[KafkaConsumer] = KafkaConsumer(
            self.topic,
            bootstrap_servers=bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset="earliest",
            consumer_timeout_ms=5000,
            enable_auto_commit=False,
            value_deserializer=lambda value: json.loads(
                value.decode("utf-8")
            )
        )

        self.logger = Logger.get_instance(
            "UserEventHistoryConsumer"
        )

    def start(self) -> None:
        """Read the complete event history and save it as JSON."""

        self.logger.info(
            f"Démarrer un consommateur historique : {self.group_id}"
        )

        events = []

        try:
            for message in self.consumer:
                event_data = message.value

                events.append({
                    "topic": message.topic,
                    "partition": message.partition,
                    "offset": message.offset,
                    "event": event_data
                })

                self.logger.debug(
                    f"Événement historique lu : "
                    f"partition={message.partition}, "
                    f"offset={message.offset}, "
                    f"type={event_data.get('event')}"
                )

            os.makedirs("output", exist_ok=True)
            filename = "output/user_events_history.json"

            with open(filename, "w", encoding="utf-8") as file:
                json.dump(
                    events,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

            self.logger.info(
                f"{len(events)} événements enregistrés dans {filename}"
            )

        except Exception as e:
            self.logger.error(
                f"Erreur: {e}",
                exc_info=True
            )

        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the consumer gracefully."""

        if self.consumer:
            self.consumer.close()
            self.logger.info("Arrêter le consommateur historique!")
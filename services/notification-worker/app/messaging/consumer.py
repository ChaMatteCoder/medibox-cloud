import json
import logging
import time
from typing import Any

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError
from pika.spec import Basic, BasicProperties

from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationConsumer:
    def start(self) -> None:
        logger.info("Starting notification worker")

        while True:
            try:
                parameters = pika.URLParameters(settings.rabbitmq_url)
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                channel.queue_declare(queue=settings.notification_queue, durable=True)
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(
                    queue=settings.notification_queue,
                    on_message_callback=self._handle_message,
                )
                logger.info("Waiting for messages on queue %s", settings.notification_queue)
                channel.start_consuming()
            except AMQPConnectionError:
                logger.warning("RabbitMQ unavailable. Retrying in 5 seconds")
                time.sleep(5)
            except KeyboardInterrupt:
                logger.info("Notification worker stopped")
                break
            except Exception:
                logger.exception("Unexpected worker error. Retrying in 5 seconds")
                time.sleep(5)

    def _handle_message(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        _properties: BasicProperties,
        body: bytes,
    ) -> None:
        try:
            message: dict[str, Any] = json.loads(body.decode("utf-8"))
            patient_id = message.get("patient_id", "desconhecido")
            event_type = message.get("event_type", "UNKNOWN")
            logger.info(
                "[NOTIFICATION] Paciente %s gerou evento %s. "
                "Alerta simulado enviado ao cuidador.",
                patient_id,
                event_type,
            )
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            logger.exception("Could not process notification message")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

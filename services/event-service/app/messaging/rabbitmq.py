import json

import pika

from app.core.config import settings


class RabbitMQPublisher:
    def publish_notification(self, message: dict) -> None:
        parameters = pika.URLParameters(settings.rabbitmq_url)
        connection = pika.BlockingConnection(parameters)
        try:
            channel = connection.channel()
            channel.queue_declare(queue=settings.notification_queue, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=settings.notification_queue,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,
                ),
            )
        finally:
            connection.close()

import logging

from app.messaging.consumer import NotificationConsumer

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logging.getLogger("pika").setLevel(logging.CRITICAL)


def main() -> None:
    NotificationConsumer().start()


if __name__ == "__main__":
    main()

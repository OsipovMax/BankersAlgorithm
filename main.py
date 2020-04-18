import pika
from banker import Banker
from worker import Worker

client_count = 3
res_count = 3


def connection_handler(decorated_func):
    def wrapper_function():
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost")
        )
        channel = connection.channel()
        decorated_func(channel)
        channel.close()
        connection.close()

    return wrapper_function


@connection_handler
def clear_rabbitmq_queues(channel):
    for i in range(1, client_count + 1):
        channel.queue_purge(queue=str(i))


@connection_handler
def create_rabbitmq_queues(channel):
    for i in range(1, client_count + 1):
        channel.queue_declare(queue=str(i))


def main():
    workers = []
    # clinets + banker
    for num in range(client_count + 1):
        worker = Worker(num, client_count, res_count)
        workers.append(worker)
        worker.start_work()
    for worker in workers:
        worker.finish_work()


if __name__ == "__main__":
    create_rabbitmq_queues()
    main()
    clear_rabbitmq_queues()

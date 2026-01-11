import random
import threading
import time
from queue import Queue

print_lock = threading.Lock()


def safe_print(message):
    with print_lock:
        print(message)


class Order:
    def __init__(self, order_id, processing_time):
        self.order_id = order_id
        self.processing_time = processing_time
        self.status = "НОВЫЙ"
        self.lock = threading.Lock()

    def update_status(self, status):
        with self.lock:
            self.status = status
            safe_print(f"[ЗАКАЗ {self.order_id}] Статус изменён: {self.status}")


class Worker(threading.Thread):
    def __init__(self, worker_id, orders_queue, machines_semaphore):
        super().__init__()
        self.worker_id = worker_id
        self.orders_queue = orders_queue
        self.machines_semaphore = machines_semaphore
        self.daemon = True

    def run(self):
        while True:
            order = self.orders_queue.get()

            if order is None:
                self.orders_queue.task_done()
                break

            safe_print(f"Работник {self.worker_id} ожидает свободную машину...")

            with self.machines_semaphore:
                safe_print(
                    f"Работник {self.worker_id} начал обработку заказа {order.order_id}"
                )
                order.update_status("В ОБРАБОТКЕ")
                time.sleep(order.processing_time)
                order.update_status("ВЫПОЛНЕН")

            self.orders_queue.task_done()


def main():
    ORDERS_COUNT = 10
    WORKERS_COUNT = 5
    MACHINES_COUNT = 3

    orders_queue = Queue()
    machines_semaphore = threading.Semaphore(MACHINES_COUNT)

    for i in range(ORDERS_COUNT):
        order = Order(i + 1, random.uniform(1, 3))
        orders_queue.put(order)

    workers = []

    for i in range(WORKERS_COUNT):
        worker = Worker(i + 1, orders_queue, machines_semaphore)
        worker.start()
        workers.append(worker)

    orders_queue.join()

    for _ in workers:
        orders_queue.put(None)

    safe_print("Все заказы успешно обработаны.")


if __name__ == "__main__":
    main()

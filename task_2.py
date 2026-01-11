import random
import threading
import time

print_lock = threading.Lock()


def safe_print(message):
    with print_lock:
        print(message)


class Session:
    def __init__(self, session_id, seats_count):
        self.session_id = session_id
        self.available_seats = seats_count
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def book_seats(self, count, user_id):
        with self.condition:
            while self.available_seats < count:
                safe_print(
                    f"Пользователь {user_id} ожидает освобождения мест "
                    f"на сеанс {self.session_id}"
                )
                self.condition.wait()

            self.available_seats -= count
            safe_print(
                f"Пользователь {user_id} забронировал {count} мест "
                f"на сеанс {self.session_id}. "
                f"Осталось мест: {self.available_seats}"
            )

    def release_seats(self, count):
        with self.condition:
            self.available_seats += count
            safe_print(
                f"Освобождено {count} мест на сеансе {self.session_id}. "
                f"Доступно: {self.available_seats}"
            )
            self.condition.notify_all()


class Cinema:
    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()

    def add_session(self, session_id, seats):
        with self.lock:
            self.sessions[session_id] = Session(session_id, seats)

    def get_session(self, session_id):
        return self.sessions[session_id]


class BookingThread(threading.Thread):
    def __init__(self, user_id, cinema, session_id, seats_count, booking_semaphore):
        super().__init__()
        self.user_id = user_id
        self.cinema = cinema
        self.session_id = session_id
        self.seats_count = seats_count
        self.booking_semaphore = booking_semaphore

    def run(self):
        with self.booking_semaphore:
            safe_print(f"Пользователь {self.user_id} начал процесс бронирования")

            session = self.cinema.get_session(self.session_id)
            session.book_seats(self.seats_count, self.user_id)

            time.sleep(random.uniform(1, 2))

            safe_print(f"Пользователь {self.user_id} завершил бронирование")
            session.release_seats(self.seats_count)


def main():
    cinema = Cinema()
    cinema.add_session("'Какой-то фильм'", 10)

    MAX_CONCURRENT_BOOKINGS = 3
    booking_semaphore = threading.Semaphore(MAX_CONCURRENT_BOOKINGS)

    threads = []
    for i in range(8):
        seats = random.randint(1, 4)
        t = BookingThread(
            user_id=i + 1,
            cinema=cinema,
            session_id="'Какой-то фильм'",
            seats_count=seats,
            booking_semaphore=booking_semaphore,
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    safe_print("Симуляция бронирования завершена.")


if __name__ == "__main__":
    main()

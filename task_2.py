import random
from typing import Dict
import time
from collections import deque


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        """
        Ініціалізує Rate Limiter.

        :param window_size: Розмір часового вікна в секундах.
        :param max_requests: Максимальна кількість повідомлень у вікні.
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_requests: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """
        Очищує застарілі запити з вікна користувача.
        Якщо після очищення вікно стає порожнім, запис про користувача видаляється.
        """
        if user_id in self.user_requests:
            window_start_time = current_time - self.window_size
            user_timestamps = self.user_requests[user_id]

            # Видаляємо всі часові мітки, що старіші за початок вікна
            while user_timestamps and user_timestamps[0] <= window_start_time:
                user_timestamps.popleft()

            # Якщо для користувача більше немає записів, видаляємо його
            if not user_timestamps:
                del self.user_requests[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """
        Перевіряє, чи може користувач надіслати повідомлення.
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        # Якщо користувача немає у списку або кількість його запитів менша за ліміт
        if user_id not in self.user_requests or len(self.user_requests.get(user_id, [])) < self.max_requests:
            return True
        return False

    def record_message(self, user_id: str) -> bool:
        """
        Записує нове повідомлення, якщо ліміт не перевищено.
        Повертає True, якщо повідомлення було успішно записано, інакше False.
        """
        if self.can_send_message(user_id):
            current_time = time.time()
            # Створюємо deque для нового користувача, якщо його немає
            if user_id not in self.user_requests:
                self.user_requests[user_id] = deque()
            # Додаємо часову мітку поточного повідомлення
            self.user_requests[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Розраховує час очікування в секундах до наступного дозволеного повідомлення.
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        # Якщо користувач може відправити повідомлення, час очікування - 0
        if user_id not in self.user_requests or len(self.user_requests[user_id]) < self.max_requests:
            return 0.0

        # Найстаріший запис у вікні
        oldest_request_time = self.user_requests[user_id][0]
        # Час, коли найстаріший запис "вийде" за межі вікна
        next_allowed_time = oldest_request_time + self.window_size

        wait_time = next_allowed_time - current_time
        return max(0.0, wait_time)


# Демонстрація роботи
def test_rate_limiter():
    """Тестова функція для перевірки роботи Rate Limiter."""
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = str(message_id % 5 + 1)

        result = limiter.record_message(user_id)
        wait_time = limiter.time_until_next_allowed(user_id)

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = str(message_id % 5 + 1)
        result = limiter.record_message(user_id)
        wait_time = limiter.time_until_next_allowed(user_id)
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
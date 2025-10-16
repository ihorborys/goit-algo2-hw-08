import random
import time
from collections import OrderedDict


# --- Частина 1: Реалізація LRU-кешу ---

class LRUCache:
    """
    Готовий клас LRU-кешу.
    OrderedDict поєднує функціональність словника та двобічно зв'язаного списку,
    що робить його ідеальним для реалізації LRU-кешу.
    """

    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: tuple) -> int:
        """
        Отримує значення за ключем. Якщо ключ існує, переміщує його
        в кінець (як останній використаний). Повертає -1, якщо ключ не знайдено.
        """
        if key not in self.cache:
            return -1
        else:
            # Перемістити елемент в кінець, щоб позначити його як нещодавно використаний
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: tuple, value: int) -> None:
        """
        Додає або оновлює пару ключ-значення. Якщо ключ вже існує, він
        оновлюється і переміщується в кінець. Якщо кеш переповнений,
        найстаріший елемент (перший) видаляється.
        """
        if key in self.cache:
            # Оновити існуючий ключ
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # Видалити найменш використовуваний елемент (перший у словнику)
            self.cache.popitem(last=False)

    def get_all_keys(self) -> list:
        """Повертає копію всіх ключів для безпечної ітерації."""
        return list(self.cache.keys())


# --- Частина 2: Реалізація функцій згідно з умовами ---

def range_sum_no_cache(array, left, right):
    """Обчислює суму елементів у діапазоні без використання кешу."""
    return sum(array[left: right + 1])


def update_no_cache(array, index, value):
    """Оновлює значення елемента в масиві без кешування."""
    array[index] = value


def range_sum_with_cache(array, left, right, cache):
    """Обчислює суму, використовуючи LRU-кеш."""
    key = (left, right)
    # Спроба отримати результат з кешу
    cached_result = cache.get(key)

    if cached_result != -1:  # Cache-hit
        return cached_result
    else:  # Cache-miss
        # Якщо в кеші немає, обчислюємо суму
        result = sum(array[left: right + 1])
        # Зберігаємо результат у кеші для майбутніх запитів
        cache.put(key, result)
        return result


def update_with_cache(array, index, value, cache):
    """Оновлює масив та інвалідує відповідні записи в кеші."""
    array[index] = value

    # Інвалідація кешу: видаляємо всі діапазони, що містять змінений індекс
    # Створюємо копію ключів, щоб уникнути помилок при зміні словника під час ітерації
    keys_to_invalidate = []
    for left, right in cache.get_all_keys():
        if left <= index <= right:
            keys_to_invalidate.append((left, right))

    for key in keys_to_invalidate:
        # Безпечно видаляємо застарілі записи
        if key in cache.cache:
            del cache.cache[key]


# --- Частина 3: Генерація запитів та тестування ---

def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    """Генерує список запитів до масиву."""
    hot = [(random.randint(0, n // 2), random.randint(n // 2, n - 1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


if __name__ == "__main__":
    # Параметри симуляції
    N = 100_000
    Q = 50_000
    K = 1_000

    # Створення початкового масиву та списку запитів
    initial_array = [random.randint(1, 100) for _ in range(N)]
    queries = make_queries(N, Q)

    # --- Тестування без кешу ---
    array_no_cache = initial_array.copy()
    start_time_no_cache = time.perf_counter()

    for query_type, arg1, arg2 in queries:
        if query_type == "Range":
            range_sum_no_cache(array_no_cache, arg1, arg2)
        elif query_type == "Update":
            update_no_cache(array_no_cache, arg1, arg2)

    end_time_no_cache = time.perf_counter()
    time_no_cache = end_time_no_cache - start_time_no_cache

    # --- Тестування з LRU-кешем ---
    array_with_cache = initial_array.copy()
    lru_cache = LRUCache(K)
    start_time_with_cache = time.perf_counter()

    for query_type, arg1, arg2 in queries:
        if query_type == "Range":
            range_sum_with_cache(array_with_cache, arg1, arg2, lru_cache)
        elif query_type == "Update":
            update_with_cache(array_with_cache, arg1, arg2, lru_cache)

    end_time_with_cache = time.perf_counter()
    time_with_cache = end_time_with_cache - start_time_with_cache

    # --- Виведення результатів ---
    speedup = time_no_cache / time_with_cache if time_with_cache > 0 else float('inf')

    print("\n--- Результати тестування ---")
    print(f"Без кешу : {time_no_cache:>6.2f} c")
    print(f"LRU-кеш  : {time_with_cache:>6.2f} c  (прискорення ×{speedup:.1f})")
import datetime
import functools
import multiprocessing
import secrets
import time
from typing import Callable

import redis

REDIS_CLIENT = redis.Redis()


class FuncAlreadyRunning(Exception):
    pass


def single(max_processing_time: datetime.timedelta) -> Callable:
    key = secrets.token_hex(16)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            r_client = REDIS_CLIENT
            lock = r_client.set(
                f"lock:{func.__name__}", key, nx=True, ex=int(max_processing_time.total_seconds())
            )
            if lock:
                result = func(*args, **kwargs)
                if r_client.get(f"lock:{func.__name__}") == key.encode():
                    r_client.delete(f"lock:{func.__name__}")
                return result
            else:
                raise FuncAlreadyRunning

        return wrapper

    return decorator


@single(max_processing_time=datetime.timedelta(seconds=5))
def process_transaction():
    time.sleep(2)
    print("I slept 2 seconds")


def task() -> None:
    global REDIS_CLIENT
    try:
        process_transaction()
    except FuncAlreadyRunning as e:
        print("Error. Function is already running!")


if __name__ == "__main__":
    print("Executing func one at a time...")
    process_transaction()
    process_transaction()
    process_transaction()
    print("Done executing one at a time!\n")

    print("Executing func in 3 processes...")
    for _ in range(3):
        p = multiprocessing.Process(target=task)
        p.start()

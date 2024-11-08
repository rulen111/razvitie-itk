import datetime
import functools
import secrets
import time
from typing import Callable

import redis

REDIS_CLIENT = None


class FuncAlreadyRunning(Exception):
    pass


def single(max_processing_time: datetime.timedelta) -> Callable:
    key = secrets.token_hex(16)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            r_client = REDIS_CLIENT
            lock = r_client.set(RESOURCE_NAME, key, nx=True, ex=int(max_processing_time.total_seconds()))
            if lock:
                result = func(*args, **kwargs)
                if r_client.get(RESOURCE_NAME) == key.encode():
                    r_client.delete(RESOURCE_NAME)
                return result
            else:
                raise FuncAlreadyRunning

        return wrapper

    return decorator


@single(max_processing_time=datetime.timedelta(seconds=5))
def process_transaction():
    time.sleep(2)
    print("I slept 2 seconds")


if __name__ == "__main__":
    if REDIS_CLIENT is None:
        REDIS_CLIENT = redis.Redis()
    RESOURCE_NAME = "main"

    print("Executing func one at a time...")
    process_transaction()
    process_transaction()
    process_transaction()
    print("Done executing one at a time!\n")

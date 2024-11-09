import datetime
import random
import time
from datetime import timedelta

import redis


class RateLimitExceed(Exception):
    pass


class RateLimiter:

    def __init__(self, client: redis.Redis, key: str, limit: int, period: timedelta):
        self.client = client
        self.key = key
        self.limit = limit
        self.period = period

    def test(self) -> bool:
        with self.client.lock("lock:" + self.key):
            count = self.client.incr(self.key)
            if count == 1:
                self.client.expire(self.key, int(self.period.total_seconds()))

            return count <= self.limit


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        pass


if __name__ == '__main__':
    r_client = redis.Redis()
    rate_limiter = RateLimiter(
        r_client, f"rate_limit:{make_api_request.__name__}", 5, datetime.timedelta(seconds=3)
    )

    for _ in range(50):
        time.sleep(random.randint(0, 1))

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")

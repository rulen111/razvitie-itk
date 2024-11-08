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
        self.client.set(self.key, self.limit, nx=True, ex=int(self.period.total_seconds()))
        limit_val = self.client.get(self.key)

        if limit_val and int(limit_val) > 0:
            self.client.decrby(self.key, 1)

            return True

        return False


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        pass


if __name__ == '__main__':
    r_client = redis.Redis()
    rate_limiter = RateLimiter(r_client, "test", 5, datetime.timedelta(seconds=3))

    for _ in range(50):
        time.sleep(random.randint(0, 1))

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")

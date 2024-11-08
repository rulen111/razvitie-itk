from typing import Optional

import redis
import json


class RedisQueue:
    """
    Simple redis queue class, supports connect, publish and consume
    """

    def __init__(self, client: redis.Redis, name: str, namespace: str = "queue"):
        self.client = client
        self.key = f"{namespace}:{name}"

    def publish(self, msg: dict):
        item = json.dumps(msg)
        self.client.rpush(self.key, item)

    def consume(self) -> Optional[dict]:
        item = self.client.lpop(self.key)
        if item is None:
            msg = None
        else:
            msg = json.loads(item)
        return msg


if __name__ == '__main__':
    r_client = redis.Redis()

    q = RedisQueue(r_client, "test")
    q.publish({'a': 1})
    q.publish({'b': 2})
    q.publish({'c': 3})

    assert q.consume() == {'a': 1}
    assert q.consume() == {'b': 2}
    assert q.consume() == {'c': 3}
    assert q.consume() is None

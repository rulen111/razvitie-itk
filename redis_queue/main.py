import redis
import json


class RedisQueue:
    """
    Simple redis queue class, supports connect, publish and consume
    """

    def __init__(self, name, namespace="queue", **redis_kwargs):
        self.__db = redis.Redis(**redis_kwargs)
        self.key = f"{namespace}:{name}"

    def publish(self, msg: dict):
        item = json.dumps(msg)
        self.__db.rpush(self.key, item)

    def consume(self) -> dict:
        item = self.__db.lpop(self.key)
        msg = json.loads(item)
        return msg


if __name__ == '__main__':
    q = RedisQueue("test")
    q.publish({'a': 1})
    q.publish({'b': 2})
    q.publish({'c': 3})

    assert q.consume() == {'a': 1}
    assert q.consume() == {'b': 2}
    assert q.consume() == {'c': 3}

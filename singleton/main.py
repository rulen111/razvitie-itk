class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonWithMeta(object, metaclass=SingletonMeta):
    pass


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance


class NotASingleton(object):
    pass


if __name__ == "__main__":
    assert NotASingleton() is not NotASingleton()

    assert SingletonWithMeta() is SingletonWithMeta()

    assert Singleton() is Singleton()

    from singleton_mod import singleton_mod
    from singleton_mod import singleton_mod as smd
    assert singleton_mod is smd

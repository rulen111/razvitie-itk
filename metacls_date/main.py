import datetime


class CreatedAtMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs["created_at"] = datetime.datetime.now()
        return super().__new__(cls, name, bases, attrs)


class MyClass(object, metaclass=CreatedAtMeta):
    pass


if __name__ == "__main__":
    myobj = MyClass()
    assert hasattr(myobj, "created_at")
    print(myobj.__getattribute__("created_at"))

import unittest

CURRENT_USER_ROLE = "moderator"


def get_user_role():
    return CURRENT_USER_ROLE


def access_control(roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            role = get_user_role()
            if role in roles:
                return func(*args, **kwargs)
            else:
                raise PermissionError("User has no access to this function")

        return wrapper

    return decorator


@access_control(roles=["admin", "moderator", "user"])
def sum(a: int, b: int) -> int:
    return a + b


@access_control(roles=["admin", "moderator"])
def sum_many(a: int, b: int, *, c: int, d: int) -> int:
    return a + b + c + d


@access_control(roles=["admin"])
def multiply(a: int, b: int) -> int:
    return a * b


class DecTestCase(unittest.TestCase):
    def test_role(self):
        self.assertEqual(get_user_role(), "moderator")

    def test_func_1(self):
        self.assertEqual(sum(1, 2), 3)

    def test_func_2(self):
        self.assertEqual(sum_many(1, 2, c=3, d=4), 10)

    def test_func_3(self):
        with self.assertRaises(PermissionError) as context:
            multiply(3, 4)

        self.assertTrue("User has no access to this function" in str(context.exception))


if __name__ == '__main__':
    unittest.main()



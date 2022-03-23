class Helper:
    def help(self):
        my_dir = self.__dir__()
        functions = []
        for x in my_dir:
            if not x.startswith('_') and x != 'help':
                functions.append(self.__getattribute__(x))

        for f in functions:
            print("{}{}:{}".format(f.__name__, f.__code__.co_varnames,
                                   f.__doc__.splitlines()[1].strip() if f.__doc__ else ''))


class TestHelper(Helper):
    def test_func1(self, some_string):
        """
        | 这是一个测试用的类
        | :some_string: Some string.
        | :return: Nothing
        """
        print("Just test fun :{}".format(some_string))

    def test_func2(self):
        """
        | 这是另一个测试用的类
        | :some_string: Some string.
        | :return: Nothing
        """
        print("Just test fun2")


if __name__ == "__main__":
    tt = TestHelper()
    tt.help()

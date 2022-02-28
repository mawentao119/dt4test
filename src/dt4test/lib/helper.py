class Helper:
    def help(self):
        mydir = self.__dir__()
        funs = []
        for x in mydir:
            if not x.startswith('__') and x != 'help':
              funs.append(self.__getattribute__(x))

        for f in funs:
            print("{}{}:{}".format(f.__name__, f.__code__.co_varnames, f.__doc__.splitlines()[1].strip()))

class testHelper(Helper):
    def test_func1(self, somestring):
        """
        | 这是一个测试用的类
        | :somestring: Some string.
        | :return: Nothing
        """
        print("Just test fun :{}".format(somestring))

    def test_func2(self):
        """
        | 这是另一个测试用的类
        | :somestring: Some string.
        | :return: Nothing
        """
        print("Just test fun2")

if __name__ == "__main__":
    tt = testHelper()
    tt.help()
from ..lib.base import Base


class TestBase:
    def test_list_to_string(self):
        bs = Base()
        alist = ["I", "am", 13]
        res = bs.list_to_string(alist, ' ')
        assert (res == "I am 13")

    def test_http_get(self):
        bs = Base()
        uid = bs.get_uuid()
        assert(uid is not None)

    def test_get_a_random_item(self):
        bs = Base()
        item1 = bs.get_a_random_item([1, 2, 3, 4, 5, 6, 7, 8])
        item2 = bs.get_a_random_item([1, 2, 3, 4, 5, 6, 7, 8])
        item3 = bs.get_a_random_item([1, 2, 3, 4, 5, 6, 7, 8])
        assert (item1 != item2 or item1 != item3)

    def test_gen_outputdir(self):
        bs = Base()
        out_dir = bs.gen_outputdir()
        assert (out_dir != "")
        assert ('_' in out_dir)

from dt4test import Base


def test_http_get():
    bs = Base()
    uid = bs.get_uuid()
    assert(uid is not None)
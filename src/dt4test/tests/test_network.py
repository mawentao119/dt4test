from ..lib.network import Network


def test_http_get():
    nt = Network()
    res = nt.send_get_request("www.baidu.com", "/", {})
    assert(200 == res.status_code)


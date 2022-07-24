import getpass
from .helper import Helper
from .network import Network
from .logger import Logger

log = Logger().get_logger(__name__)

class CaseRunner(Helper):
    """
    Run Test Case
    """

    def __init__(self):
        self.network = Network()

    def run_pytest(self, cases):
        """
        API 运行 pytest 用例 ： TODO: 进一步调试和优化参数支持和稳定性
        """
        user_name = getpass.getuser()
        payload = {"method": "api_pytest",
                   "category": "case",
                   "apiuser": user_name,
                   "key": cases}
        res = self.network.send_post_request("127.0.0.1:8080", "/api/v1/task/", payload)
        s = bytes.decode(res.content)
        return s

    def run_rftest(self, cases):
        """
        API 运行 rf 用例 ： TODO: 进一步调试和优化参数支持和稳定性
        """
        user_name = getpass.getuser()
        payload = {"method": "api_rf",
                   "category": "case",
                   "apiuser": user_name,
                   "key": cases}
        res = self.network.send_post_request("127.0.0.1:8080", "/api/v1/task/", payload)
        s = bytes.decode(res.content)
        return s


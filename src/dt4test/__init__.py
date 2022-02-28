from .lib.logger import Logger
from .lib.network import Network
from .lib.base import Base
from .lib.jsonp import JsonP
from .lib.config_ini import ConfigIni
from .lib.case_runner import CaseRunner

log = Logger().get_logger()
base = Base()
network = Network()
config_ini = ConfigIni()
jsonp = JsonP()
case_runner = CaseRunner()

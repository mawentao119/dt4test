import os
import sys
from shutil import copyfile

from ..lib.helper import Helper
from ..lib.logger import Logger

log = Logger().get_logger(__name__)


def show_cli_help():
    """
    显示 客户端帮助
    """
    print(">> resource create myres[.py] : 创建自己的资源库")
    print(">> create resource myres[.py] : 创建自己的资源库")


class Resource(Helper):
    """
    外部Resource资源的管理模块,暂不对外使用
    """
    def __init__(self, resource_subdir='resource'):

        self.resource_subdir = resource_subdir  # 用于操作 ini 配置文件
        self.project_dir = os.environ.get("PROJECT_DIR", "/tmp")
        self.resource_dir = os.path.join(self.project_dir, self.resource_subdir)
        self.template_file = os.path.join(os.path.dirname(__file__), 'resource_template.py')
        log.info("Resource 资源目录：{}".format(self.resource_dir))

    def cli(self, argv: []):
        """
        客户端接口程序
        """
        if len(argv) < 4:
            show_cli_help()
            return 0

        if len(argv) == 4:
            if argv[1] == 'create' and argv[2] == 'resource':
                return self.create_resource(argv[3])
            if argv[1] == 'resource' and argv[2] == 'create':
                return self.create_resource(argv[3])

        print("无法解析的参数：{}".format(argv))
        show_cli_help()
        return -1

    def get_user_resource(self):
        """
        取得用户自定义的Lib信息：${PROJECT_DIR}/resource 下的模块
        """
        user_res = {}
        user_res_dir = self.resource_dir
        if os.path.exists(user_res_dir):
            alist = [x for x in os.listdir(user_res_dir) if x.endswith('.py') and not x.startswith('_')]
            if len(alist) == 0:
                return
            sys.path.append(user_res_dir) if user_res_dir not in sys.path else None
            for py in alist:
                mod_file = os.path.splitext(py)[0]
                mod_imp = __import__(mod_file)
                if not hasattr(mod_imp, 'MODULE_NAME'):        # 没有这个变量，人为是普通的pyfile ，不作为 dt 的模块使用
                    continue
                mod_name = mod_imp.MODULE_NAME
                if not hasattr(mod_imp, 'MODULE_INSTANCE'):
                    continue
                mod_instance = mod_imp.MODULE_INSTANCE
                user_res[mod_name] = mod_instance
        return user_res

    def create_resource(self, resource_name='myres'):
        """
        创建用户 resource 模板

        | :param resource_name: 模板名，不要到 ``.py`` 后缀
        | :return: 模板文件路径
        """
        user_res_dir = self.resource_dir
        os.makedirs(user_res_dir) if not os.path.exists(user_res_dir) else None
        res_name = resource_name
        if not res_name.endswith('.py'):
            res_name = res_name + '.py'

        res_file = os.path.join(user_res_dir, res_name)

        if os.path.exists(res_file):
            print("文件已经存在，请删除或另起名字 :{} ".format(res_file))
            return -1

        copyfile(self.template_file, res_file)

        print("创建成功，请修改文件中的 TODO :{}".format(res_file))
        return 0

    def get_resource_dir(self):
        return self.resource_dir


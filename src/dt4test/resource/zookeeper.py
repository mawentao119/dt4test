import json

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError
from kazoo.protocol.states import KeeperState

from ..lib.helper import Helper
from ..lib.logger import Logger

logger = Logger().get_logger(__name__)


def check_zk_connect_state(func):
    """
    用于检测zk连接状态的装饰器，如果连接断开则重连
    """
    def wrapper(*args, **kwargs):

        # print(args)

        # _zk为MyZK实例
        _zk = args[0]

        if _zk.zk_client.client_state != KeeperState.CONNECTED:
            print("***** 重新连接zk *****")
            _zk.connect_zk()

        return func(*args, **kwargs)

    return wrapper


def check_zk_node_if_exists(func):
    """
    用于检测zk节点是否存在的装饰器
    """
    def wrapper(*args, **kwargs):

        # print(args)
        # print(kwargs)

        # _zk为MyZK实例， node为MyZK各函数输入的node参数
        _zk = args[0]
        if "path" in kwargs:
            node = kwargs["path"]
        else:
            node = args[1]

        if not _zk.zk_node_if_exists(node):
            raise NoNodeError("The ZK node '%s' not exists, please check it! " % node)

        return func(*args, **kwargs)

    return wrapper


class ZooKeeper(Helper):
    """
    使用 ``kazoo`` 操作 zookeeper，可以使用 ``ZooKeeper()`` 构造实例 或 ``zookeeper`` 实例连接
    """

    def __init__(self):
        self.zk_client = None
        self.hosts = "not set"
        self.kwargs = None

    def init(self, hosts, **kwargs):
        self.set_hosts(hosts)
        self.set_args(**kwargs)
        self.zk_client = KazooClient(hosts, **kwargs)

    def set_hosts(self, hosts):
        """
        设置hosts
        """
        self.hosts = hosts

    def set_args(self, **kwargs):
        """
        设置客户端参数kwargs
        """
        self.kwargs = kwargs

    def zk_start(self):
        """
        启动客户端
        """
        self.zk_client.start()

    def zk_stop(self):
        """
        停止客户端
        :return:
        """
        self.zk_client.stop()

    def connect_zk(self):
        """
        修改参数后，用于zk的重新连接
        """
        self.zk_client = KazooClient(self.hosts, **self.kwargs)
        self.zk_client.start()

    def zk_node_if_exists(self, path):
        """
        若节点存在，返回zk节点信息；若节点不存在，返回None
        """
        return self.zk_client.exists(path)

    @check_zk_connect_state
    @check_zk_node_if_exists
    def zk_get(self, path=""):
        """
        根据zk path获取数据
        """
        logger.info("获取节点 %s 的数据" % path)
        data, stat = self.zk_client.get(path)
        print("Version: %s, data: %s" % (stat.version, data.decode("utf-8")))

        self.zk_stop()
        return data.decode("utf-8")

    @check_zk_connect_state
    @check_zk_node_if_exists
    def zk_get_children(self, path=""):
        """
        根据指定zk节点获取其子节点
        """
        logger.info("获取节点 %s 的子节点" % path)
        children_nodes = self.zk_client.get_children(path)
        print("There are %s children with names %s" % (len(children_nodes), children_nodes))

        self.zk_stop()
        return children_nodes

    @check_zk_connect_state
    def zk_create_node(self, path):
        """
        创建节点
        """
        res = self.zk_client.ensure_path(path)
        self.zk_stop()

        return res

    @check_zk_connect_state
    def zk_create_node_and_set_data(self, path, data, **kwargs):
        """
        | 创建节点，并赋值。如果makepath设置为False，父节点不存在时创建会报错，所以将makepath设置为True
        | :param path: 新节点
        | :param data: 新节点对应的数据，需是bytes类型，如果输入的是字典，需要先进行json.dumps()操作
        | :return: 新节点的路径
        """
        if type(data) is dict:
            data = json.dumps(data)
        if type(data) is not bytes:
            data = data.encode()

        if "makepath" in kwargs:
            # 不接受外部输入的makepath参数
            del kwargs["makepath"]

        if self.zk_node_if_exists(path):
            res = self.zk_update_data(path, data)
        else:
            res = self.zk_client.create(path, data, makepath=True, **kwargs)

        self.zk_stop()
        return res

    @check_zk_connect_state
    @check_zk_node_if_exists
    def zk_update_data(self, path, data, **kwargs):
        """
        | 更新节点数据
        | :param path: 节点
        | :param data: 节点对应的数据，需是bytes类型，如果输入的是字典，需要先进行json.dumps()操作
        | :return: 返回zk节点信息
        """
        if type(data) is dict:
            data = json.dumps(data)
        if type(data) is not bytes:
            data = data.encode()

        print("***** update zk node {} data to {} *****".format(path, data))
        res = self.zk_client.set(path, data, **kwargs)

        self.zk_stop()
        return res

    @check_zk_connect_state
    @check_zk_node_if_exists
    def zk_delete_node(self, path, recursive=False):
        """
        | :param path: 节点
        | :param recursive： 是否递归删除子节点，默认选择False
        | :return: 如果删除成功则返回为True
        """
        logger.warning("***** delete zk node: %s !" % path)
        res = self.zk_client.delete(path, recursive=recursive)

        self.zk_stop()
        return res


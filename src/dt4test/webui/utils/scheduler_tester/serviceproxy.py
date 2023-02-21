# -*- utf-8 -*-

###############################################################
# Service Interface for performing service query
# __author__ = "mawentao119@gmail.com"
# __datetime__ = "2023-02-12 12:43:00"
###############################################################

import os

from utils.common import load_single_module_from_path, load_class_from_name
from utils.mylogger import getlogger

log = getlogger(__name__)


class ServiceProxy():
    """
    业务代理接口
    :name: service name like iegg, us, guldan, yarn
    :method: api ,batch
    :service_dir: where is the [service]_service.py
    :service: real service class lazy loaded
    """
    def __init__(self):
        self.name = "unknown"
        self.method = "unknown"
        self.isRefreshed = False
        self.service_dir = "unknown"
        self.service = None

    def set_refreshed(self, state=True):
        self.isRefreshed = state

    def set_service_dir(self, path: str):
        self.service_dir = path

    def get_service_method(self):
        return self.method

    def get_service_dir(self):
        return self.service_dir

    def set_service_name(self, name):
        self.name = name

    def set_service_method(self, method):
        self.method = method

    def init_service(self, service_dir=os.path.join(os.environ.get("PROJECT_DIR", "unknown"), "service"), service_file=""):
        """
        动态加载业务的类实现，提供真正的业务返回结果
        :return: service instance or None and info
        """

        if self.isRefreshed:
            return False, "业务已经加载过了"

        if not os.path.exists(service_dir):
            info = "无法加载业务模块，目录不存在：{}".format(service_dir)
            log.error(info)
            return False, info

        if service_file != "":
            load_file = service_file
        else:
            load_file = "service.py"

        if not os.path.exists(os.path.join(service_dir, load_file)):
            info = "无法加载业务模块，文件不存在：{}".format(service_dir)
            log.error(info)
            return False, info

        log.info("尝试加载业务 dir:{} name:{}".format(service_dir, load_file))
        try:
            is_mod_loaded = load_single_module_from_path(service_dir, load_file)
            if not is_mod_loaded:
                info = "加载业务模块失败：path:{} file:{}".format(service_dir, load_file)
                log.error(info)
                return False,info

            mod, py = service_file.rsplit('.', 1)
            service_class = load_class_from_name(mod + ".Service")

            if not service_class:
                info = "无法识别类：{}".format(mod + ".Service")
                log.error(info)
                return False, info

            self.service = service_class()

            self.isRefreshed = True
            self.service_dir = service_dir
            self.name = self.service.get_name()

            info = "业务加载完成： {}".format(self.name)
            log.info(info)
            return True, info
        except Exception as e:
            err_info = "业务加载异常：{}".format(e)
            log.error(err_info)
            return None, err_info

    def get_task_ids(self, want_num=100):
        """
        返回需要收集的Task id
        :want_num: 需要返回多少个taskid
        :return: [taskid1, taskid2]
        """
        if self.isRefreshed:
            return self.service.get_task_ids(want_num)
        else:
            log.warn("业务还没有初始化")
            return []

    def get_tasks_ids(self, want_num=100):
        return self.get_task_ids(want_num)

    def get_inst_ids(self, task_id, insts_per_task):
        """
        返回需要收集的task id 's Instants id
        :return: [instid1, instid2]
        """
        if self.isRefreshed:
            return self.service.get_inst_ids(task_id, insts_per_task)
        else:
            log.warn("业务还没有初始化")
            return []

    def get_insts_ids(self,task_id, insts_per_task):
        return self.get_inst_ids(task_id, insts_per_task)

    def get_task_info(self, task_id):
        """
        get task detail info using task structure.
        :param task_id:
        :return: {"taskid":"1231233",{{}}}
        """
        if self.isRefreshed:
            return self.service.get_task_info(task_id)
        else:
            log.warn("业务还没有初始化")
            return {}

    def get_inst_info(self, inst_id):
        """
        get instance detail info
        :param inst_id:
        :return: {"instid":"sdfsd",{}}
        """
        if self.isRefreshed:
            return self.service.get_inst_info(inst_id)
        else:
            log.warn("业务还没有初始化")
            return {}

    def get_instance_info(self, inst_id):
        return self.get_inst_info(inst_id)

    def get_tasks(self):
        if self.isRefreshed:
            return self.service.get_tasks()
        else:
            log.warn("业务还没有初始化")
            return []

    def get_insts(self):
        if self.isRefreshed:
            return self.service.get_insts()
        else:
            log.warn("业务还没有初始化")
            return []

    def get_instances(self):
        return self.get_insts()

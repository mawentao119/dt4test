# -*- utf-8 -*-

###############################################################
# Scheduler backend check rules proxy
# __author__ = "mawentao119@gmail.com"
# __datetime__ = "2023-02-13 17:43:00"
###############################################################
import os
import time
from threading import Thread
from utils.common import load_modules_from_path, load_single_module_from_path, load_class_from_name, get_time_now
from utils.mylogger import getlogger

log = getlogger(__name__)

class ServiceProxy():
    """
    rules: check rule
    rules_info: record rules check result
    records: check records
    mistakes: problems found
    schechdler: data of scheduler
    """
    def __init__(self, scheduler):

        self.name = "unknown"
        self.service_dir = "unknown"
        self.isRefreshed = False
        self.service = None

        self.update_interval = 5 * 60   # 5min
        self.need_do = True

        self.is_updating = False

        self.sc = scheduler

    def get_update_interval(self):
        return self.update_interval

    def set_update_interval(self, new_value):
        log.info("设置数据更新时间:{}秒".format(new_value))
        self.update_interval = int(new_value)
        return True

    def get_need_do(self):
        return self.need_do

    def start_update(self):
        if self.is_updating:
            return False

        self.need_do = True
        log.info("开始数据周期性更新...")
        self.service_update_runner()

        return True

    def stop_update(self):
        self.need_do = False
        log.info("停止周期性数据更新...")
        return True

    def clear_data(self):
        try:
            self.service.clear_data()
        except Exception as e:
            log.warn("业务没有提供clear_data，用默认的")
            self._clear_data()

    def set_refreshed(self, state=True):
        self.isRefreshed = state

    def get_service_dir(self):
        return self.service_dir

    def get_service_name(self):
        return self.name

    def init_service(self, service_dir=os.path.join(os.environ.get("PROJECT_DIR", "unknown"), "service"),
                     service_file="", clear_data=False):
        """
        动态加载业务的类实现，提供真正的业务返回结果
        :return: service instance or None and info
        """

        if self.isRefreshed:
            if not clear_data:
                return False, "业务已经加载过了,请使用clear_data标志进行初始化"
            else:
                log.warn("业务即将重新初始化")

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
                return False, info
        except Exception as e:
            err_info = "业务模块加载异常：{}".format(e)
            log.error(err_info)
            return None, err_info

        try:
            mod, py = service_file.rsplit('.', 1)
            service_class = load_class_from_name(mod + ".Service")

            if not service_class:
                info = "无法识别类：{}".format(mod + ".Service")
                log.error(info)
                return False, info

            self.service = service_class(self.sc)

            self.isRefreshed = True
            self.service_dir = service_dir

        except Exception as e:
            err_info = "模块加载完成，业务加载异常：{}".format(e)
            log.error(err_info)
            return None, err_info

        try:
            self.name = self.service.get_name()
        except Exception as e:
            info = "尝试方法 get_name 失败，跳过"
            log.warn(info)

        try:
            self.update_interval = self.service.get_update_interval()
        except Exception as e:
            info = "尝试方法 get_update_interval 失败，使用默认值 {}".format(self.update_interval)
            log.warn(info)

        if clear_data:
            try:
                self.service.clear_data()
            except Exception as e:
                info = "尝试方法 clear_date 失败，使用默认方法"
                log.warn(info)
                self._clear_data()

        info = "业务加载完成： {}".format(self.name)
        log.info(info)
        return True, info

    def update_one_task(self, task_id):
        """
        get task detail info using task structure.
        :param task_id:
        :return: {"taskid":"1231233",{{}}}
        """
        if self.isRefreshed:
            return self.service.update_one_task(task_id)
        else:
            log.warn("业务还没有初始化，无法添加task")
            return False

    def update_one_inst(self, inst_id):
        """
        get instance detail info
        :param inst_id:
        :return: {"instid":"sdfsd",{}}
        """
        if self.isRefreshed:
            return self.service.update_one_inst(inst_id)
        else:
            log.warn("业务还没有初始化")
            return False

    def update_tasks(self):
        log.info("update tasks ...")
        if self.isRefreshed:
            return self.service.update_tasks()
        else:
            log.warn("业务还没有初始化")
            return False

    def update_insts(self):
        log.info("update insts ...")
        if self.isRefreshed:
            return self.service.update_insts()
        else:
            log.warn("业务还没有初始化")
            return False

    def update_data(self):
        return self.update_tasks() and self.update_insts()

    def update_instances(self):
        return self.update_insts()

    def _clear_data(self):
        log.info("清除所有数据")
        return self.sc.clear_data()

    def clear_tasks(self):
        log.info("清除Tasks数据")
        return self.service.clear_tasks()

    def clear_insts(self):
        log.info("清除Insts数据")
        return self.service.clear_insts()

    def service_update_loop(self):

        self.is_updating = True

        while True:
            interval = self.get_update_interval()
            time.sleep(interval)

            need_do = self.get_need_do()
            if need_do:
                log.info("开始 Data Update:{} ...".format(get_time_now()))
                self.service.update_tasks()
                self.service.update_insts()
                log.info("结束 Update date:{}".format(get_time_now()))
            else:
                log.warn("** No need do update **")
                break

        self.is_updating = False

    def service_update_runner(self):
        run_all_runner = Thread(target=self.service_update_loop, args=())
        run_all_runner.start()
        return run_all_runner


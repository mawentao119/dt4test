# -*- utf-8 -*-

###############################################################
# Test Scheduler system, backend checker
# __author__ = "mawentao119@gmail.com"
# __datetime__ = "2023-02-11 17:43:00"
###############################################################

from datetime import datetime
from .serviceproxy import ServiceProxy

from utils.common import get_size, get_time_now
from utils.mylogger import getlogger


log = getlogger(__name__)


class Scheduler():
    """
    Gets all tasks and Instances and repeatedly update the information
    Tasks: All the collected tasks by add_task()
           {
           "task_id1":[
                        {"t1":{task_id1_info}},
                        {"t1":{task_id1_info}}
                        ],
           "task_id2":[]
            }
    Insts: All the collected instances.
           {
           "instance_id1":[
                        {"t1":{instance_id1_info}},
                        {"t1":{instance_id1_info}}
                        ],
           "instance_id2":[]
            }
    """

    def __init__(self, MaxTasks=10, MaxInsts=100):
        self.Tasks = {}
        self.Insts = {}
        self.MaxTasks = MaxTasks
        self.MaxInsts = MaxInsts
        self.starttime = "{}".format(get_time_now())

        self.service = ServiceProxy()

    def init_service(self, service_dir, service_file="service.py"):
        return self.service.init_service(service_dir, service_file)

    def update_max_tasks(self, new_value=1000):
        self.MaxTasks = new_value
        return self.MaxTasks

    def update_max_insts(self, new_value=10000):
        self.MaxInsts = new_value
        return self.MaxInsts

    def get_start_time(self):
        return self.starttime

    def get_time_now(self):
        return get_time_now()

    def get_exist_tasks_num(self):
        return len(self.Tasks.keys())

    def get_exist_insts_num(self):
        return len(self.Insts.keys())

    def clear_tasks(self):
        self.Tasks.clear()
        return True

    def clear_insts(self):
        self.Insts.clear()
        return True

    def add_task_batch(self, tasks_want_added: int, insts_per_task: int):
        """
        :param newadd:
        :param insts_per_task:
        :return: tasks, Instances
        """
        cur_tasks = self.get_exist_tasks_num()
        gap = self.MaxTasks - cur_tasks
        if gap > tasks_want_added:
            need_add_task_num = tasks_want_added
            log.info("Tasks: {} ,MaxTasks:{} , wanted:{}".format(cur_tasks, self.MaxTasks, tasks_want_added))
        else:
            need_add_task_num = gap
            log.warn("无法全部增加，Tasks: {},MaxTasks:{}, want:{}, actual:{}".format(cur_tasks,
                                                                               self.MaxTasks, tasks_want_added,
                                                                               need_add_task_num))

        if need_add_task_num > 0:
            cur_insts_num = self.get_exist_insts_num()
            inst_gap = self.MaxInsts - cur_insts_num
            if inst_gap <= 0:
                log.error("无法增加任务，实例已满：Instance:{}, Maxinstance:{}".format(cur_insts_num, self.MaxInsts))
                return 0, inst_gap  # added tasks, Instances

            tasks_added = 0
            insts_added = 0
            task_ids = self.service.get_task_ids(self.get_exist_tasks_num() + need_add_task_num)  # 多要一些id，避免重复
            for task_id in task_ids:
                if task_id in self.Tasks.keys():  # 如果任务已经存在则跳过
                    log.warn("任务已经存在：{}".format(task_id))
                    continue

                tasks_added += self._update_a_task(task_id, self.service.get_task_info(task_id))

                insts_ids = self.service.get_inst_ids(task_id, insts_per_task)
                for i, inst_id in enumerate(insts_ids):
                    added = self.add_inst(inst_id)
                    insts_added += added
                    if inst_gap - added <= 0:
                        return tasks_added, insts_added

                    if i + 1 >= insts_per_task:  # 如果满足一次最大实例数，跳出当前 task
                        break

            return tasks_added, insts_added

    def add_inst(self, inst_id):
        inst = self.service.get_inst_info(inst_id)
        return self._update_a_inst(inst_id, inst)

    def _update_a_inst(self, inst_id, inst):
        """
        Inst增加，内存的核心变更，可能膨胀，需要小心操作
        :param inst_id:
        :param inst:
        :return:
        """
        t = get_time_now()
        if inst_id in self.Insts.keys():
            if len(self.Insts[inst_id]) > 0:
                [latest_val] = self.Insts[inst_id][-1].values()
                if inst == latest_val:                           # {t:{inst}} ==>  {new} vs {inst}
                    return 0
                else:
                    # log.info("Inst变更 new vs old: \n {} VS \{}".format(inst, self.Insts[inst_id][-1]))
                    self.Insts[inst_id].append({t: inst})
                    return 1
            else:
                self.Insts[inst_id].append({t: inst})
                return 1
        else:
            self.Insts[inst_id] = []
            self.Insts[inst_id].append({t: inst})
            # log.info("Inst增加\n {}".format(inst))
            return 1

    def _update_a_task(self, task_id, task):
        """
        Task增加，内存的核心变更，可能膨胀，需要小心操作
        :param task_id:
        :param task:
        :return:
        """
        t = get_time_now()
        if task_id in self.Tasks.keys():
            if len(self.Tasks[task_id]) > 0:
                [latest_val] = self.Tasks[task_id][-1].values()
                if task == latest_val:
                    return 0
                else:
                    # log.debug("Task变更 new vs old: \n {} VS \{}".format(task, self.Tasks[task_id][-1]))
                    self.Tasks[task_id].append({t: task})
                    return 1
            else:
                self.Tasks[task_id].append({t: task})
                return 1
        else:
            self.Tasks[task_id] = []
            self.Tasks[task_id].append({t: task})
            return 1

    def add_task_by_id(self, task_id, insts_per_task=50):
        taskadded = self._update_a_task(task_id, self.service.get_task_info(task_id))
        instance_ids = self.service.get_inst_ids(task_id, insts_per_task)
        instadded = 0
        for iid in instance_ids:
            if instadded < insts_per_task:
                instadded += self._update_a_inst(iid, self.service.get_inst_info(iid))
            else:
                break
        return taskadded, instadded

    def remove_task(self, task_id):
        return self.Tasks.pop(task_id)

    def remove_inst(self, inst_id):
        return self.Insts.pop(inst_id)

    def get_task_ids(self):
        return self.Tasks.keys()

    def get_task_record(self, task_id):
        return self.Tasks.get(task_id, [])

    def get_inst_record(self, inst_id):
        return self.Insts.get(inst_id, [])

    def get_tasks_bytes(self):
        log.info("Get Task Size started :{}".format(get_time_now()))
        l = get_size(self.Tasks)
        log.info("Get Task Size finished :{}".format(get_time_now()))
        return l

    def get_insts_bytes(self):
        log.info("Get Insts Size started :{}".format(get_time_now()))
        l = get_size(self.Insts)
        log.info("Get Insts Size finished :{}".format(get_time_now()))
        return l

    def update_data(self, mode="each_all"):
        """
        周期性的更新Tasks 和 Instance
        :return:
        """
        log.info("开始数据更新，mode:{}".format(mode))

        affected_tasks = 0
        affected_insts = 0

        if mode == "task_each":
            affected_tasks = self.update_tasks_each()
        elif mode == "inst_each":
            affected_insts = self.update_insts_each()
        elif mode == "each_all":
            affected_tasks = self.update_tasks_each()
            affected_insts = self.update_insts_each()

        elif mode == "task_batch":
            affected_tasks = self.update_tasks_batch()
        elif mode == "inst_batch":
            affected_insts = self.update_insts_batch()
        elif mode == "batch_all":
            affected_tasks = self.update_tasks_batch()
            affected_insts = self.update_insts_batch()

        return affected_tasks, affected_insts

    def update_tasks_each(self):
        """
        有限扫描任务进行更新，逐个进行
        TODO：新增实例的补充
        :return:
        """
        log.info("开始each更新Tasks：{}".format(get_time_now()))
        affected_tasks = 0
        for tid in self.Tasks.keys():
            task = self.service.get_task_info(tid)
            affected_tasks += self._update_a_task(tid, task)
        log.info("结束each更新Tasks：{}".format(get_time_now()))
        return affected_tasks

    def update_insts_each(self):
        """
        有限扫描实例进行更新，逐个扫描
        :return:
        """
        log.info("开始each更新Insts：{}".format(get_time_now()))
        affected_insts = 0
        for iid in self.Insts.keys():
            inst = self.service.get_inst_info(iid)
            affected_insts += self._update_a_task(iid, inst)
        log.info("结束each更新Insts：{}".format(get_time_now()))
        return affected_insts

    def update_tasks_batch(self):
        """
        批量更新tasks
        :return:
        """
        log.info("开始batch更新Tasks：{}".format(get_time_now()))
        affected_tasks = 0
        tasks = self.service.get_tasks()
        for t in tasks:
            task_id = t.get("task_id", None)
            if not task_id:
                log.error("数据格式异常，找不到 task_id:{}".format(t))
                continue
            affected_tasks += self._update_a_task(task_id, t)

        log.info("结束batch更新Tasks：{}".format(get_time_now()))
        return affected_tasks

    def update_insts_batch(self):
        """
        批量更新 insts
        :return:
        """
        log.info("开始batch更新Insts：{}".format(get_time_now()))
        affected_insts = 0
        insts = self.service.get_insts()
        for i in insts:
            inst_id = i.get("instance_id")
            if not inst_id:
                log.error("数据格式异常，找不到 instance_id:{}".format(i))
                continue
            affected_insts += self._update_a_inst(inst_id, i)
        log.info("结束batch更新Insts：{}".format(get_time_now()))
        return affected_insts

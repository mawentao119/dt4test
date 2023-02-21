# -*- utf-8 -*-

###############################################################
# Test Scheduler system, backend checker
# __author__ = "mawentao119@gmail.com"
# __datetime__ = "2023-02-11 17:43:00"
###############################################################

from utils.common import get_size, get_time_now
from utils.mylogger import getlogger


log = getlogger(__name__)


class TimeServerData():
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

    def __init__(self):
        self.Tasks = {}
        self.Insts = {}
        self.starttime = "{}".format(get_time_now())

    def get_start_time(self):
        return self.starttime

    def get_time_now(self):
        return get_time_now()

    def get_exist_tasks_num(self):
        return len(self.Tasks.keys())

    def get_exist_insts_num(self):
        return len(self.Insts.keys())

    def clear_tasks(self):
        log.info("clear tasks ...")
        self.Tasks.clear()
        return True

    def clear_insts(self):
        log.info("clear insts ...")
        self.Insts.clear()
        return True

    def clear_data(self):
        log.info("clear data ...")
        self.clear_insts()
        self.clear_tasks()
        return True

    def update_one_inst(self, inst_id, inst):
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

    def update_one_task(self, task_id, task):
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

    def remove_task(self, task_id):
        log.info("remove task {}".format(task_id))
        if task_id in self.Tasks.keys():
            return self.Tasks.pop(task_id)
        return {}

    def remove_inst(self, inst_id):
        log.info("remove inst {}".format(inst_id))
        if inst_id in self.Insts.keys():
            return self.Insts.pop(inst_id)
        return {}

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

    def update_tasks(self, tasks):
        """
        批量更新tasks
        :return:
        """
        log.info("开始batch更新Tasks：{}".format(get_time_now()))
        affected_tasks = 0
        for t in tasks:
            task_id = t.get("task_id", None)
            if not task_id:
                log.error("数据格式异常，找不到 task_id:{}".format(t))
                continue
            affected_tasks += self.update_one_task(task_id, t)

        log.info("结束batch更新Tasks：{}".format(get_time_now()))
        return affected_tasks

    def update_insts(self, insts):
        """
        批量更新 insts
        :return:
        """
        log.info("开始batch更新Insts：{}".format(get_time_now()))
        affected_insts = 0

        for i in insts:
            inst_id = i.get("inst_id")
            if not inst_id:
                log.error("数据格式异常，找不到 inst_id:{}".format(i))
                continue
            affected_insts += self.update_one_inst(inst_id, i)
        log.info("结束batch更新Insts：{}".format(get_time_now()))
        return affected_insts

# -*- utf-8 -*-

###############################################################
# This is an example service interface
# __author__ = "mawentao119@gmail.com"
# __datetime__ = "2023-02-12 12:43:00"
###############################################################

import random

class Service:

    def __init__(self, scheduler):
        self.name = "IEGG Test"
        self.mode = "each"
        self.sc = scheduler

    def get_name(self):
        """
        用于标识不同的业务接口
        :return:
        """
        return self.name

    def get_mode(self):
        """
        如果 mode 是each，则使用each更新方式，如果是 batch 则使用batch更新方式
        :return:
        """
        return self.mode

    def get_task_index(self, task_id):
        """
        用于测试报告中自动生成任务的连接
        :param task_id:
        :return:
        """
        return "https://106.52.253.136:8080/tdw/guldan/#/devops/taskInfo?taskId=" + str(task_id) + "&locale=cn"

    def update_one_task(self, task_id):
        """
        返回一个任务的具体信息.
        :param task_id:
        :return: {"taskid":"1231233",{{}}}
        """
        res = {"task_id":"t1","project_id":123,"para":{"x":"x1","y":"y1"}}
        return self.sc.update_one_task(task_id, res)

    def update_one_inst(self, inst_id):
        """
        返回实例的具体信息
        :param inst_id:
        :return: {"instid":"sdfsd",{}}
        """
        res = {"inst_id": "iid1", "project_id": 123, "para": {"x": "i1", "y": "y1"}}
        return self.sc.update_one_inst(inst_id, res)

    def update_tasks(self):
        """
        批量返回任务的信息，可以调用 sc的接口，也可以直接关数据
        直接关数据，需要自己控制数据的去重，和校验
        :return:
        """
        tm = self.sc.get_time_now()
        tasks = {
            "t1": {
                tm: {"task_id": "t1", "project_id": 123, "para":{"x": "x1","y": "y1"}}
            },
            "t2": {
                tm: {"task_id": "t2", "project_id": 123, "para": {"x": "x2", "y": "y2"}}
            }
        }

        self.sc.Tasks = tasks

        return True

    def update_insts(self):
        """
        批量返回实例，不应该包含重复的 inst_id
        :return:
        """
        res = [{"inst_id": "iid1", "state": random.randint(1, 10), "para": {"x": "i1", "y": "y1"}},
                {"inst_id": "iid2", "state": random.randint(1, 10), "para": {"x": "i2", "y": "y2"}}]
        for i in res:
            iid = i.get("inst_id", "unknown")
            self.sc.update_one_inst(iid, i)
        return True

    def clear_data(self):
        """
        清除数据，最好调用sc接口，也可以直接操作 sc.Tasks 和 sc.Insts
        :return:
        """
        return self.sc.clear_data()

    def clear_tasks(self):
        return self.sc.clear_tasks()

    def clear_insts(self):
        return self.sc.clear_insts()


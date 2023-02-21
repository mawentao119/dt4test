# -*- utf-8 -*-

###############################################################
# This is an example service interface
# __author__ = "mawentao119@gmail.com"
# __datetime__ = "2023-02-12 12:43:00"
###############################################################

class Service:

    def __init__(self):
        self.name = "IEGG Test"
        self.method = "api"

    def get_name(self):
        """
        用于标识不同的业务接口
        :return:
        """
        return self.name

    def get_task_index(self, task_id):
        """
        用于测试报告中自动生成任务的连接
        :param task_id:
        :return:
        """
        return "https://106.52.253.136:8080/tdw/guldan/#/devops/taskInfo?taskId=" + str(task_id) + "&locale=cn"

    def get_task_ids(self, want_num=100):
        """
        返回需要收集的Task id
        :want_num: 需要返回多少个taskid
        :return: [taskid1, taskid2]
        """
        return ['t1','t2']

    def get_inst_ids(self, task_id, insts_per_task):
        """
        返回需要收集的task id 's Instants id
        :return: [instid1, instid2]
        """
        return ['iid1','iid2']

    def get_task_info(self, task_id):
        """
        返回一个任务的具体信息.
        :param task_id:
        :return: {"taskid":"1231233",{{}}}
        """
        if task_id == "t1":
            return {"task_id":"t1","project_id":123,"para":{"x":"x1","y":"y1"}}
        else:
            return {"task_id": "t2", "project_id": 123, "para": {"x": "x2", "y": "y2"}}

    def get_inst_info(self, inst_id):
        """
        返回实例的具体信息
        :param inst_id:
        :return: {"instid":"sdfsd",{}}
        """
        if inst_id == "iid1":
            return {"inst_id": "iid1", "project_id": 123, "para": {"x": "i1", "y": "y1"}}
        else:
            return {"inst_id": "iid2", "project_id": 123, "para": {"x": "i2", "y": "y2"}}

    def get_instance_info(self, inst_id):
        return self.get_inst_info(inst_id)

    def get_tasks(self):
        """
        批量返回任务的信息
        :return:
        """
        return [{"task_id":"t1","project_id":123,"para":{"x":"x1","y":"y1"}},
                {"task_id": "t2", "project_id": 123, "para": {"x": "x2", "y": "y2"}}]

    def get_insts(self):
        return [{"inst_id": "iid1", "project_id": 123, "para": {"x": "i1", "y": "y1"}},
                {"inst_id": "iid2", "project_id": 123, "para": {"x": "i2", "y": "y2"}}]

    def get_instances(self):
        return self.get_insts()


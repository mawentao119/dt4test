# -*- utf-8 -*-

###############################################################
# Test Rules, backend checker
# __author__ = "mawentao119@gmail.com"
# __datetime__ = "2023-02-12 12:43:00"
###############################################################

class Rule():
    def __init__(self, scheduler):
        self.author = "charisma"
        self.desc = "检查实例状态变更是否正常"

        self.sc = scheduler

        self.report = {"pass": 0,
                       "fail": []}      # a fail: {id:taskid_instid, desc, info}  id用于组装结果报告

    def get_desc(self):
        """
        生成报告的时候或许会用到
        :return:
        """
        return self.desc

    def run_check(self):                       # 不要带其他参数，只是使用类自己的参数
        for iid in self.sc.Insts.keys():
            state_list = []
            for i in self.sc.Insts[iid]:       # time:{}  time:{}
                [st] = i.values()
                state_list.append(int(st["state"]))  # pending ,running ,fininshed

            res = check_inst_state(state_list)
            if res == 0:
                self.report["pass"] += 1
            if res == 1:
                self.gen_fail_record(iid, state_list)

        return self.do_report()

    def gen_fail_record(self, inst_id, state_list):
        self.report["fail"].append({"time": self.sc.get_time_now(),
                                    "id": "unknown" + "_" +inst_id,
                                    "desc": self.desc,
                                    "info": ",".join([str(s) for s in state_list])})      # 不用带name和info，占内存

    def do_report(self):
        return self.report


def check_inst_state(state_list):
    """
    检查实例的状态变更过程是否符合状态机逻辑
    :param state_list:
    :return: -1 miss rule ; 0 pass ; 1 fail
    """
    if len(state_list) <= 1 :
        return -1
    for i in range(0, len(state_list)-1):
        if state_list[i+1] - state_list[i] < 0:
            return 1
    return 0



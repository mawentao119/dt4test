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

from .scheduler_data import TimeServerData

log = getlogger(__name__)

class CheckRules():
    """
    rules: check rule
    rules_info: record rules check result
    records: check records
    mistakes: problems found
    schechdler: data of scheduler
    """
    def __init__(self, scheduler: TimeServerData):
        self.rules = {}     # [ {"rule_name": rule_cls} ]
        self.rule_records = {}   # ["rule_name":{runtimes, pass, fail}]
        self.scheduler = scheduler
        self.mistakes = {}  # {"id_rulename":{info}}  # id_rulename 用于去重复
        self.check_interval = 5 * 60    # 5min default

        self.need_do = True    # do check or not
        self.is_checking = False   # checking is running

        self.rule_dir = "unknown"

    def get_check_interval(self):
        return self.check_interval

    def set_check_interval(self, new_value):
        log.info("设置check时间间隔,{}秒".format(new_value))
        self.check_interval = int(new_value)
        return new_value

    def get_need_do(self):
        return self.need_do

    def stop_do_check(self):
        self.need_do = False
        log.info("停止周期性规则检查...")
        return True

    def start_do_check(self):
        if self.is_checking:
            return False

        self.need_do = True
        log.info("开始周期性规则检查")
        self.do_check_runner()

        return True

    def clear_mistakes(self):
        log.warn("清除mistakes表信息")
        self.mistakes.clear()
        return True

    def clear_rule_records(self):
        log.info("清除rule_records信息")
        self.rule_records.clear()
        return True

    def clear_rules(self):
        log.info("清除所有rule")
        self.rules.clear()
        return True

    def add_rule_to_rule_records(self, rule_name):
        self.rule_records[rule_name] = {"runtimes": 0,
                                        "pass": 0,
                                        "fail": 0}

    def update_rules(self, rule_dir=os.path.join(os.environ.get("PROJECT_DIR", "unknown"), "rules")):
        """
        add rules to self.rules from pyfile
        :return:
        """
        log.info("更新Rules：dir: {}".format(rule_dir))

        if not os.path.exists(rule_dir):
            return 0, "rules目录不存在:{}".format(rule_dir)

        self.clear_rules()  # 删除调rules

        try:
            loaded_mod = load_modules_from_path(rule_dir)
        except Exception as e:
            info = "加载rule失败: {}".format(rule_dir)
            log.error(info)
            return 0, info

        for mod in loaded_mod:
            class_name = mod + ".Rule"
            try:
                log.info("尝试加载Rule：{}".format(class_name))
                rule_class = load_class_from_name(class_name)
            except Exception as e:
                log.error("异常:无法识别的类：{}".format(class_name))
                continue
            if not rule_class:
                log.error("跳过:无法识别的类：{}".format(class_name))
                continue
            self.rules[class_name] = rule_class
            log.info("成功加载Rule：{}".format(class_name))
        return len(self.rules), "加载完成"

    def add_one_rule(self, rule_file, rule_dir=os.path.join(os.environ.get("PROJECT_DIR", "unknown"), "rules")):
        if not os.path.exists(rule_dir):
            return 0, "rules目录不存在:{}".format(rule_dir)

        try:
            isloaded = load_single_module_from_path(rule_dir, rule_file)
        except Exception as e:
            info = "加载rule失败: {}".format(rule_dir)
            log.error(info)
            return False, info

        mod, py = rule_file.rsplit('.', 1)
        if isloaded:
            try:
                mod_cls = load_class_from_name(mod + ".Rule")
            except Exception as e:
                info = "异常:无法识别的类：{} {}".format(mod + ".Rule", e)
                return False, info
            self.rules[mod + ".Rule"] = mod_cls

        return True, "加载完成".format(mod + ".Rule")

    def remove_one_rule(self, rule_name):
        if rule_name in self.rules.keys():
            return self.rules.pop(rule_name)
        else:
            return {"info":"rule: {} 不存在".format(rule_name)}

    def add_report(self, rule_name, report):
        """
        记录rule执行信息及出错的任务或实例
        :param report:    { "time": self.sc.get_time_now(),
                            "task_id": "unknown",
                            "inst_id": inst_id,
                            "info": ",".join(state_list)}
        :param rule_name: rule
        :return:
        """
        passed = report.get("pass", None)
        if passed is None:
            log.error("规则返回错误，找不到 pass ：{}".format(rule_name))
            return False
        fail_list = report.get("fail", None)
        if fail_list is None:
            log.error("规则返回错误，找不到 fail ：{}".format(rule_name))
            return False

        failed = len(report.get("fail"))

        if failed > 0:
            for f in report["fail"]:
                f_id = f["id"] + "#" + rule_name
                log.error(">>{}:{}".format(f_id, f))
                self.mistakes[f_id] = f

        self.update_rule_records(rule_name, passed, failed)

    def update_rule_records(self, rule_name, passed, failed):

        if rule_name not in self.rule_records.keys():
            self.add_rule_to_rule_records(rule_name)

        self.rule_records[rule_name]["runtimes"] += 1
        self.rule_records[rule_name]["pass"] += passed
        self.rule_records[rule_name]["fail"] += failed

        return True

    def do_check(self):
        """
        Run rules
        :return:
        """
        # self.update_rules()
        for name, cls in self.rules.items():
            inst = cls(self.scheduler)
            log.info("执行 rule {}:{}".format(name, get_time_now()))
            self.add_report(name, inst.run_check())
            log.info("完成 rule {}:{}".format(name, get_time_now()))

    def run_all_rule(self):
        self.do_check()

    def run_one_rule(self, rule_name):
        for name, cls in self.rules.items():
            if name != rule_name:
                continue
            inst = cls(self.scheduler)
            log.info("执行 rule {}:{}".format(name, get_time_now()))
            report = name, inst.run_check()
            log.info("完成 rule {}:{}".format(name, get_time_now()))
            return report

        log.error("找不到rule ：{}".format(rule_name))
        return {}

    def get_report(self):
        for fail_id, info in self.mistakes.items():
            log.error("**{}:{}".format(fail_id, info))
        return self.mistakes

    def get_rule_report(self, rule_name):
        if rule_name in self.rule_records.keys():
            return self.rule_records[rule_name]
        return {}

    def get_all_rule(self):
        return self.rules.keys()

    def do_check_loop(self):
        self.is_checking = True
        while True:
            interval = self.get_check_interval()
            need_do = self.get_need_do()
            time.sleep(interval)
            log.info("Start CheckRule Update:{} ...".format(get_time_now()))
            if need_do:
                self.do_check()
            else:
                log.warn("** No need do rule check **")
                break
            log.info("Finished CheckRule Update:{}".format(get_time_now()))

        self.is_checking = False

    def do_check_runner(self):
        cr_runner = Thread(target=self.do_check_loop, args=())
        cr_runner.start()
        return cr_runner

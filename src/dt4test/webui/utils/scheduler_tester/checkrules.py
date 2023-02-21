# -*- utf-8 -*-

###############################################################
# Scheduler backend check rules proxy
# __author__ = "mawentao119@gmail.com"
# __datetime__ = "2023-02-13 17:43:00"
###############################################################
import os

from utils.common import load_modules_from_path, load_single_module_from_path, load_class_from_name, get_time_now
from utils.mylogger import getlogger

from .scheduler import Scheduler

log = getlogger(__name__)

class CheckRules():
    """
    rules: check rule
    rules_info: record rules check result
    records: check records
    mistakes: problems found
    schechdler: data of scheduler
    """
    def __init__(self, scheduler: Scheduler):
        self.rules = {}     # [ {"rule_name": rule_cls} ]
        self.rule_records = {}   # ["rule_name":{runtimes, pass, fail}]
        self.scheduler = scheduler
        self.mistakes = []

        self.rule_dir = "unknown"

    def add_rule_to_rule_records(self, rule_name):
        self.rule_records[rule_name] = {"runtimes": 0,
                                        "pass": 0,
                                        "fail": 0}

    def update_rules(self, rule_dir=os.path.join(os.environ.get("PROJECT_DIR", "unknown"), "rules")):
        """
        add rules to self.rules from pyfile
        :return:
        """
        if not os.path.exists(rule_dir):
            return 0, "rules目录不存在:{}".format(rule_dir)

        try:
            loaded_mod = load_modules_from_path(rule_dir)
        except Exception as e:
            info = "加载rule失败: {}".format(rule_dir)
            log.error(info)
            return 0, info

        for mod in loaded_mod:
            try:
                rule_class = load_class_from_name(mod + ".Rule")
            except Exception as e:
                log.error("异常:无法识别的类：{}".format(mod + ".Rule"))
                continue
            if not rule_class:
                log.error("跳过:无法识别的类：{}".format(mod + ".Rule"))
                continue
            self.rules[mod + ".Rule"] = rule_class
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

    def add_rule_report(self, rule_name, report):
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
        failed = len(report.get("fail"))

        if failed > 0:
            for f in report["fail"]:
                self.mistakes.append(f)

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
        self.update_rules()
        for name, cls in self.rules:
            inst = cls(self.scheduler)
            log.info("Run rule {}:{}".format(inst.get_name(), get_time_now()))
            self.add_rule_report(name, inst.runcheck())
            log.info("Done rule {}:{}".format(inst.get_name(), get_time_now()))

    def get_report(self):
        return self.mistakes

    def get_rule_report(self, rule_name):
        return self.rule_records[rule_name]


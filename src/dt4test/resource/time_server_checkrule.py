#################################################################
# poster is the cia client for transfer files and run command in remote opernats.
# using `dt4test poster` command ,assisting with dtagent,using server to transfer commands
#################################################################

import json
import os.path
import requests
from urllib3 import encode_multipart_formdata

from ..lib.network import Network as nt
from ..lib.helper import Helper
from ..lib.logger import Logger


log = Logger().get_logger(__name__)


class CheckRule(Helper):
    """
    Poster for cia
    """
    def __init__(self, host="127.0.0.1", port="8081"):
        self.host = host
        self.port = port
        self.data_path = "/api/v1/tsc/"
        self.rule_path = "/api/v1/tcr/"
        self.tasklist_path = "/api/v1/task_list/"
        self.addr = "http://" + host + ":" + port

        self.conf_file = "/tmp/webui.info"     #  ip:port the `dt webui start` will create this file

        if os.path.exists(self.conf_file):
            self.init(self.conf_file)

    def init(self, conf_file):
        """
        For cli invoker, using conf_file to init host,port
        :param conf_file: Should be like 12.12.12.12:8081
        :return: None
        """
        if not os.path.exists(conf_file):
            log.error("找不到配置文件:".format(conf_file))
            log.error("配置文件格式:   ip:port ".format(conf_file))
            exit(1)

        # TODO: Add try-except for ValueError
        with open(conf_file, 'r') as cf:
            line = cf.readline().strip()
            self.host, self.port = line.split(":")
            self.addr = "http://" + self.host + ":" + self.port

    def get_data_path(self):
        return self.data_path

    def get_rule_path(self):
        return self.rule_path

    def get_addr(self):
        return self.addr

    def update_rule(self, rule_dir=""):
        if rule_dir == "":
            payload = {"method": "update_rule"}
        else:
            payload = {"method": "update_rule", "rule_dir": rule_dir}

        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status":"fail", "msg":"return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def add_checkrule_update_job(self, min, sec, mode="each_all"):
        payload = {"method": "add_scheduler_data_update_job", "min":min, "sec": sec, "mode": mode}
        res = nt.send_post_request(self.addr, self.tasklist_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def add_one_rule(self, rule_file, rule_dir):
        payload = {"method": "add_one_rule", "rule_file": rule_file, "rule_dir": rule_dir}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def remove_one_rule(self, rule_name):
        payload = {"method": "remove_one_rule", "rule_name": rule_name}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def run_one_rule(self, rule_name):
        payload = {"method": "run_one_rule", "rule_name": rule_name}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def run_all_rule(self):
        payload = {"method": "run_all_rule"}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def get_all_rule(self):
        payload = {"method": "get_all_rule"}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def get_report(self):
        payload = {"method": "get_report"}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def get_rule_report(self, rule_name):
        payload = {"method": "get_rule_report", "rule_name": rule_name}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def get_check_interval(self):
        payload = {"method": "get_check_interval"}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def set_check_interval(self, interval):
        payload = {"method": "set_check_interval", "interval": interval}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def get_need_do(self):
        payload = {"method": "get_need_do"}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def stop_do_check(self):
        payload = {"method": "stop_do_check"}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def start_do_check(self):
        payload = {"method": "start_do_check"}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def clear_mistakes(self):
        payload = {"method": "clear_mistakes"}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def clear_rule_records(self):
        payload = {"method": "clear_rule_records"}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def clear_rules(self):
        payload = {"method": "clear_rules"}
        res = nt.send_post_request(self.addr, self.rule_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def cli(self, argv: []):
        """
        客户端接口程序
        """
        log.info("Argv: {}".format(','.join(argv)))
        if len(argv) == 2:
            show_cli_help()
            return 0

        if argv[2] == "update_rule":
            if len(argv) == 4:
                return self.update_rule(argv[3])
            else:
                return self.update_rule()
        elif argv[2] == "add_one_rule":
            return self.add_one_rule(argv[3], argv[4])
        elif argv[2] == "remove_one_rule":
            return self.remove_one_rule(argv[3])
        elif argv[2] == "run_one_rule":
            return self.run_one_rule(argv[3])
        elif argv[2] == "run_all_rule":
            return self.run_all_rule()
        elif argv[2] == "get_all_rule":
            return self.get_all_rule()
        elif argv[2] == "get_report":
            return self.get_report()
        elif argv[2] == "get_check_interval":
            return self.get_check_interval()
        elif argv[2] == "set_check_interval":
            return self.set_check_interval(argv[3])
        elif argv[2] == "get_need_do":
            return self.get_need_do()
        elif argv[2] == "stop_do_check":
            return self.stop_do_check()
        elif argv[2] == "start_do_check":
            return self.start_do_check()
        elif argv[2] == "clear_mistakes":
            return self.clear_mistakes()
        elif argv[2] == "clear_rule_records":
            return self.clear_rule_records()
        elif argv[2] == "clear_rules":
            return self.clear_rules()

        else:
            print("无法解析的参数：{}".format(argv))
            show_cli_help()
            return -1


def show_cli_help():
    """
    显示 客户端帮助
    """
    print(">> cr update_rule [rule_dir]: 更新rule信息, 没有参数则使用系统默认目录")
    print(">> cr add_one_rule rule_file rule_dir: 增加单独一个rule")
    print(">> cr remove_one_rule rule_name: 删除一个rule,可以通过 get_all_rule 查看rules")
    print(">> cr run_one_rule rule_name: 运行一个rule")
    print(">> cr run_all_rule :运行所有rule")
    print(">> cr get_all_rule :取得系统中所有的rule")
    print(">> cr get_report :显示检查出来的错误信息")
    print(">> cr get_check_interval :查看当前check间隔时间")
    print(">> cr set_check_interval interval:设置check间隔时间,单位:秒")
    print(">> cr get_need_do :是否循环运行check")
    print(">> cr stop_do_check :停止循环执行check")
    print(">> cr start_do_check :开始循环执行check")
    print(">> cr clear_mistakes :清除目前查出来的错误信息")
    print(">> cr clear_rule_records :清除rule的检查记录")
    print(">> cr clear_rules :删除所有rule")


if __name__ == "__main__":
    cr = CheckRule()
    # res = poster.get_env()
    # print(res)
    res = cr.put_command('cmd', 'role1', "sleep 2")
    print(res)

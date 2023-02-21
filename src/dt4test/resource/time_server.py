#################################################################
# poster is the cia client for transfer files and run command in remote opernats.
# using `dt4test poster` command ,assisting with dtagent,using server to transfer commands
#################################################################

import json
import os.path

from ..lib.network import Network as nt
from ..lib.helper import Helper
from ..lib.logger import Logger


log = Logger().get_logger(__name__)


def show_cli_help():
    """
    显示 客户端帮助
    """
    print(">> sd get_rule_path :查看rule目录")
    print(">> sd get_start_time :取得系统启动时间")
    print(">> sd remove_task taskid :删除任务")
    print(">> sd remove_inst instid :删除实例")
    print(">> sd get_insts_bytes :取得当前insts数据大小")
    print(">> sd get_tasks_bytes :取得当前tasks数据大小")


class TimeServerData(Helper):
    """
    Poster for cia
    """
    def __init__(self, host="127.0.0.1", port="8081"):
        self.host = host
        self.port = port
        self.path = "/api/v1/tsc/"
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

    def get_api_path(self):
        return self.path

    def get_rule_path(self):
        return self.rule_path

    def get_addr(self):
        return self.addr

    def get_start_time(self):
        payload = {"method": "get_start_time"}
        res = nt.send_post_request(self.addr, self.path, json=payload)
        if not res.status_code == 200:
            return {"status":"fail", "msg":"return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def remove_task(self, task_id):
        payload = {"method": "remove_task", "task_id": task_id}
        res = nt.send_post_request(self.addr, self.path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def remove_inst(self, inst):
        payload = {"method": "remove_inst", "inst_id": inst}
        res = nt.send_post_request(self.addr, self.path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def get_insts_bytes(self):
        payload = {"method": "get_insts_bytes"}
        res = nt.send_post_request(self.addr, self.path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def get_tasks_bytes(self):
        payload = {"method": "get_tasks_bytes"}
        res = nt.send_post_request(self.addr, self.path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def get_task_record(self, task_id):
        payload = {"method": "get_task_record", "task_id": task_id}
        res = nt.send_post_request(self.addr, self.path, json=payload)
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

        if argv[2] == "get_rule_path":
            return self.get_rule_path()
        elif argv[2] == "get_start_time":
            return self.get_start_time()
        elif argv[2] == "remove_task":
            return self.remove_task(argv[3])
        elif argv[2] == "remove_inst":
            return self.remove_inst(argv[3])
        elif argv[2] == "get_insts_bytes":
            return self.get_insts_bytes()
        elif argv[2] == "get_tasks_bytes":
            return self.get_tasks_bytes()
        else:
            print("无法解析的参数：{}".format(argv))
            show_cli_help()
            return -1


if __name__ == "__main__":
    sc = TimeServerData()
    # res = poster.get_env()
    # print(res)
    res = sc.put_command('cmd', 'role1', "sleep 2")
    print(res)

    # res = poster.upload_file('role1','/Users/mawentao/PycharmProjects/data-test/dt4test/src/dt4test/webui/utils/temp_up/1.sh', '/Users/mawentao/PycharmProjects/data-test/dt4test/src/dt4test/webui/utils/temp_down/s.sh')
    # print(res)

    # res = poster.put_command('ufile_a', 'role1', "/Users/mawentao/PycharmProjects/data-test/dt4test/src/dt4test/webui/utils/temp_up/1.sh")
    # print(res)

    # res = poster.download_command_file("1115205907_811", "/Users/mawentao/PycharmProjects/data-test/dt4test/src/dt4test/webui/utils/temp_down/x.zip")
    # print(res)
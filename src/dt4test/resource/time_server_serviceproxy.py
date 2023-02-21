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


class ServiceProxy(Helper):
    """
    Poster for cia
    """
    def __init__(self, host="127.0.0.1", port="8081"):
        self.host = host
        self.port = port
        self.data_path = "/api/v1/tsc/"
        self.service_path = "/api/v1/tsv/"
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

    def get_service_path(self):
        return self.service_path

    def get_addr(self):
        return self.addr

    def update_data(self):
        payload = {"method": "update_data"}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
        if not res.status_code == 200:
            return {"status":"fail", "msg":"return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def add_scheduler_data_update_job(self, min, sec, mode="each_all"):
        payload = {"method": "add_scheduler_data_update_job", "min":min, "sec": sec, "mode": mode}
        res = nt.send_post_request(self.addr, self.tasklist_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def update_one_task(self, task_id):
        payload = {"method": "add_one_task", "task_id": task_id}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def update_one_inst(self, inst_id):
        payload = {"method": "add_one_inst", "inst_id": inst_id}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def init_service(self, service_dir, service_file="service.py", clear_data=False):
        payload = {"method": "init_service",
                   "service_dir": service_dir,
                   "service_file": service_file,
                   "clear_data": clear_data}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def clear_data(self):
        payload = {"method": "clear_data"}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def clear_tasks(self):
        payload = {"method": "clear_tasks"}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def clear_insts(self):
        payload = {"method": "clear_insts"}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def del_task(self, task_id):
        payload = {"method": "del_task", "task_id": task_id}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def del_inst(self, inst_id):
        payload = {"method": "del_inst", "inst_id": inst_id}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def get_update_interval(self):
        payload = {"method": "get_update_interval"}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def set_update_interval(self, interval):
        payload = {"method": "set_update_interval", "interval": interval}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def get_need_do(self):
        payload = {"method": "get_need_do"}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def start_update(self):
        payload = {"method": "start_update"}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def stop_update(self):
        payload = {"method": "stop_update"}
        res = nt.send_post_request(self.addr, self.service_path, json=payload)
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

        if argv[2] == "init_service":
            service_dir = argv[3]
            service_file = argv[4]
            if len(argv) == 5:
                clear_data = False
            elif argv[5] == "F":
                clear_data = False
            else:
                clear_data = True
            return self.init_service(service_dir, service_file, clear_data)
        if argv[2] == "get_service_path":
            return self.get_service_path()
        if argv[2] == "update_data":
            return self.update_data()
        if argv[2] == "add_one_task":
            task_id = argv[3]
            return self.update_one_task(task_id)
        if argv[2] == "add_one_inst":
            task_id = argv[3]
            inst_id = argv[4]
            return self.update_one_inst(inst_id)
        if argv[2] == "clear_data":
            return self.clear_data()
        if argv[2] == "clear_tasks":
            return self.clear_tasks()
        if argv[2] == "clear_insts":
            return self.clear_insts()
        if argv[2] == "del_task":
            task_id = argv[3]
            return self.del_task(task_id)
        if argv[2] == "del_inst":
            inst_id = argv[3]
            return self.del_inst(inst_id)
        if argv[2] == "get_update_interval":
            return self.get_update_interval()
        if argv[2] == "set_update_interval":
            interval = argv[3]
            return self.set_update_interval(interval)
        if argv[2] == "get_need_do":
            return self.get_need_do()
        if argv[2] == "start_update":
            return self.start_update()
        if argv[2] == "stop_update":
            return self.stop_update()

        print("无法解析的参数：{}".format(argv))
        show_cli_help()
        return -1


def show_cli_help():
    """
    显示 客户端帮助
    """
    print(">> sv init_service service_dir servicefile [T|F]:初始化业务模块,模块目录，模块文件名，是否清除数据")
    print(">> sv get_service_path :取得业务模块目录")
    print(">> sv update_data :进行一次数据更新")
    print(">> sv add_one_task taskid :增加一个task")
    print(">> sv add_one_inst instid :增加一个inst")
    print(">> sv clear_data :清除数据")
    print(">> sv clear_tasks :清除任务数据")
    print(">> sv clear_insts :清除实例数据")
    print(">> sv del_task taskid :删除一个task")
    print(">> sv del_inst instid:删除一个inst")
    print(">> sv get_need_do :是否循环执行update")
    print(">> sv get_update_interval :取得循环执行update周期，单位：秒")
    print(">> sv set_update_interval interval:设置循环执行update周期，单位：秒")
    print(">> sv start_update :启动周期性update任务")
    print(">> sv stop_update :停止周期性update任务")


if __name__ == "__main__":
    sc = ServiceProxy()

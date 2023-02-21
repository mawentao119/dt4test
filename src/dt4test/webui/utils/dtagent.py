# -*- utf-8 -*-
import os
import sys
import time
import json
import requests
from urllib3 import encode_multipart_formdata
from threading import Thread

from dt4test import network as nt
from dt4test import proc


class DtAgent():
    """
    cia代理
    部署在每个实例或者container中，连接cia server，完成所有收到的命令的执行
    主要是接受 其他agent发过来的请求，cia server 进行转发
    完成文件的传输，远程命令的执行，以及测试环境拓扑的构建
    """
    def __init__(self, cia_ip, cia_port, role_info):
        """

        :param cia_ip:
        :param cia_port:
        :param role_info:   role1:group1,role2:group2
        """
        self.server_host = "http://" + cia_ip + ":" + cia_port
        self.api_path = "/api/v1/cia/"

        self.log_size = 100
        self.log = []
        self.cur_idx = -1
        self.init_log()

        self.hb_interval = 3     # heart beat interval default is 3

        self.roles_info = role_info

        self.roles = []
        self.role_ids = []
        self.group_roles = []
        self.roles_str = ""
        self.get_roles()

    def init_log(self):
        for i in range(0, self.log_size):
            self.log.append('x')

    def get_server(self):
        return self.server_host

    def get_path(self):
        return self.api_path

    def get_roles(self):
        self.group_roles = self.roles_info.split(",")
        for s in self.group_roles:
            self.roles.append(s.split(':')[0])
        self.roles_str = ','.join(self.roles)

    def get_ids_str(self):
        return ','.join(self.role_ids)

    def put_command(self, target, cmd_type, cmd_arg):
        payload = {"method":"put_command", "cmd_type": cmd_type, "target":target, "cmd_arg":cmd_arg}
        res = nt.send_post_request(self.server_host, self.api_path, payload)
        if not res.status_code == 200:
            return {"status":"fail", "msg":"return code:{}".format(res.status_code),"cmd_id": "0"}
        body = json.loads(res.text)
        return body

    def get_command(self):
        info = self.get_info()
        role_ids = self.get_ids_str()
        payload = {"method":"get_command", "role_ids": role_ids, "info": info}
        res = nt.send_post_request(self.server_host, self.api_path, json=payload)
        if not res.status_code == 200:
            return {"status":"fail", "msg":"return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def get_info(self):
        return "TODO"

    def set_interval(self, sec):
        self.hb_interval = sec

    def get_interval(self):
        return self.hb_interval

    def put_result(self, payload):
        res = nt.send_post_request(self.server_host, self.api_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def get_result(self, cmd_id):
        payload = {"method": "get_result", "cmd_id": cmd_id}
        res = nt.send_post_request(self.server_host, self.api_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def register(self, local_ip='unknown'):
        payload = {"method": "register", "group_roles": ','.join(self.group_roles), "ip": local_ip}
        res = nt.send_post_request(self.server_host, self.api_path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        role_ids = body["role_ids"]
        self.role_ids = role_ids
        print("RegisterOK, role_ids: {}".format(self.role_ids))
        return body

    def is_registered(self):
        return True if len(self.role_ids) > 0 else False

    def add_log(self, info):
        self.cur_idx += 1
        if self.cur_idx < self.log_size:
            self.log[self.cur_idx] = str(self.cur_idx) + ": " + info
        else:
            self.cur_idx = -1
            self.add_log(info)

    def get_log(self, format='str'):
        if format == "str":
            info = ""
            head = self.cur_idx + 1
            while head < self.log_size:
                info += self.log[head] + "\n"
                head += 1

            head = 0
            while head <= self.cur_idx:
                info += self.log[head] + "\n"
                head += 1

            return info
        else:
            return self.log


def runner(agent, cmd):
    print("Run CMD: {}".format(cmd))
    cmd_type = cmd["cmd_type"]
    cmd_arg = cmd["cmd_arg"]

    if cmd_type == 'cmd':
        print("执行命令:cmd:{}".format(cmd))
        result = proc.run_process(cmd_arg, shell=True)
        payload = {"method": "put_result",
                   "sub_id": cmd["sub_id"],
                   "role_id": cmd["role_id"],
                   "cmd_id": cmd["cmd_id"],
                   "ret_code": "{}".format(result.rc),
                   "out": "{}".format(result.stdout),
                   "err": "{}".format(result.stderr)}
        print("Put Result:{}".format(payload))
        agent.put_result(payload)
    elif cmd_type == 'ufile_a':
        print("上传文件:upload_a:{}".format(cmd))
        payload = {"method": "put_result",
                   "sub_id": cmd["sub_id"],
                   "role_id": cmd["role_id"],
                   "cmd_id": cmd["cmd_id"],
                   "ret_code": "0",
                   "out": "down",
                   "err": ""}
        if not os.path.exists(cmd_arg):
            payload["ret_code"] = "1"
            payload["err"] = "Can not find: {}".format(cmd_arg)
            agent.put_result(payload)
            return
        if not os.path.isfile(cmd_arg):
            payload["ret_code"] = "2"
            payload["err"] = "Not a file: {}".format(cmd_arg)
            agent.put_result(payload)
            return

        file_path, file_name = os.path.split(cmd_arg)
        file_name = cmd["role_id"] + '-' + file_name
        with open(cmd_arg, 'rb') as f:
            file = {
                "files": (file_name, f.read()),
                "method": "upload_a",
                "target": cmd["role_id"],
                "des_path": cmd["cmd_id"]
            }
            encode_data = encode_multipart_formdata(file)
            file_data = encode_data[0]
            header = {"Content-Type": encode_data[1]}
            res = requests.post(agent.get_server() + agent.get_path(), headers=header, data=file_data)
        if not res.status_code == 201:
            payload["ret_code"] = "3"
            payload["err"] = "upload file err {}:{}".format(res.status_code, cmd_arg)
            agent.put_result(payload)
        else:
            agent.put_result(payload)

    elif cmd_type == "dfile_a":
        # down laod file from server
        print("下载文件:upload_a:{}".format(cmd))
        payload = {"method": "put_result",
                   "sub_id": cmd["sub_id"],
                   "role_id": cmd["role_id"],
                   "cmd_id": cmd["cmd_id"],
                   "ret_code": "0",
                   "out": "down",
                   "err": ""}

        file = {
            "files": ("my_name", "x"),
            "method": "download_a",
            "target": cmd["role_id"],
            "des_path": cmd["cmd_id"]  # 获取 /tmp/cmd_id/xxxx
        }
        encode_data = encode_multipart_formdata(file)
        file_data = encode_data[0]
        header = {"Content-Type": encode_data[1]}

        url = agent.get_server() + agent.get_path()

        try:

            with requests.post(url, headers=header, data=file_data, stream=True) as r:
                r.raise_for_status()
                file_path, file_name = os.path.split(cmd_arg)  # 目标文件
                os.makedirs(file_path) if not os.path.exists(file_path) else None
                with open(cmd_arg, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        # if chunk:
                        f.write(chunk)
        except Exception:
            payload["ret_code"] = "4"
            payload["out"] = "Failed"
            payload["err"] = "Download or write file fail:{}".format(cmd_arg)
        finally:
            agent.put_result(payload)


def show_usage():
    print(">>python dtagent.py cia_ip, cia_port, role_info")
    print(">>role_info format: role1:group1,role2:group2")


if __name__ == '__main__':
    if len(sys.argv) < 4:
        show_usage()
        exit(1)
    cia_ip = sys.argv[1]
    cia_port = sys.argv[2]
    role_info = sys.argv[3]
    agent = DtAgent(cia_ip, cia_port, role_info)
    interval = agent.get_interval()

    my_pid = os.getpid()
    print("Write pid file: /tmp/dtagant.pid ...")
    with open('/tmp/dtagent.pid', 'w') as pf:
        pf.write("{}".format(my_pid))

    local_ip = nt.get_local_ip()

    for i in range(0, 60):
        try:
            result = agent.register(local_ip)
            if agent.is_registered():
                print("Agent register Success:{}".format(result))
                break
            else:
                print("Agent register failed , try again later ...")
                agent.add_log("Register failed")
                time.sleep(interval)
        except Exception:
            print("Connection Error , try again later ...")
            time.sleep(interval)

    if not agent.is_registered():
        print("Failed: Agent register failed for many times retry ...")
        exit(1)

    while True:
        time.sleep(interval)
        # print("{} : Get Cmd".format(time.time()))
        res = agent.get_command()
        cmds = res["cmds"]
        print("CMDS:{}".format(cmds))
        for cmd in cmds:
            agent.add_log("sent cmd :{}".format(cmd))
            task = Thread(target=runner, args=(agent, cmd))
            task.run()




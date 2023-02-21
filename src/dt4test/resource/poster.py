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


def show_cli_help():
    """
    显示 客户端帮助
    """
    print(">> poster env :显示所有环境组件的信息")
    print(">> poster _role :显示所有role的信息")
    print(">> poster _role[1] cmd \"command\" :远程执行命令")
    print(">> poster cmd_id :数字1开头，查询cmd_id的任务结果")
    print(">> poster drop cmd_id :放弃命令")
    print(">> poster clear :清除所有命令")
    print(">> poster _role ufile_a|cfile remote/file.txt :按role收集文件")
    print(">> poster dfile cmd_id local_file.zip: 下载收集到的文件")
    print(">> poster _role ufile|sfile file_path des_path: 上传文件到role, des_path要包含文件名")
    print(">> poster : 显示使用信息")
    print(">> 配置文件 /tmp/poster.cfg 内容 IP:PORT")


class Poster(Helper):
    """
    Poster for cia
    """
    def __init__(self, host="127.0.0.1", port="8081"):
        self.host = host
        self.port = port
        self.path = "/api/v1/cia/"
        self.file_path = "/api/v1/cia_file"
        self.addr = "http://" + host + ":" + port

        self.role_ids = []
        self.group_roles = ["poster"]

        self.conf_file = "/tmp/poster.cfg"     #  ip:port

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

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_api_path(self):
        return self.path

    def get_file_api_path(self):
        return self.file_path

    def get_addr(self):
        return self.addr

    def get_role_ids(self):
        return self.role_ids

    def register(self):
        payload = {"method": "register", "group_roles": ','.join(self.group_roles), "ip": nt.get_local_ip()}
        res = nt.send_post_request(self.addr, self.path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        role_ids = body["role_ids"]
        self.role_ids = role_ids
        log.info("RegisterOK, role_ids: {}".format(self.role_ids))
        return body

    def get_env(self):
        payload = {"method": "get_env"}
        res = nt.send_post_request(self.addr, self.path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def get_targets(self, target: str):
        payload = {"method": "get_target", "target": target}
        res = nt.send_post_request(self.addr, self.path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def put_command(self, cmd_type, target, cmd_arg):
        payload = {"method":"put_command", "cmd_type": cmd_type, "target": target, "cmd_arg": cmd_arg}
        res = nt.send_post_request(self.addr, self.path, json=payload)
        if not res.status_code == 200:
            return {"status":"fail", "msg":"return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def send_command(self, cmd_type, target, cmd_arg):
        return self.put_command(cmd_type, target, cmd_arg)

    def get_result(self, cmd_id):
        payload = {"method":"get_result", "cmd_id": cmd_id}
        res = nt.send_post_request(self.addr, self.path, json=payload)
        if not res.status_code == 200:
            return {"status":"fail", "msg":"return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def drop_command(self, cmd_id):
        payload = {"method": "drop_command", "cmd_id": cmd_id}
        res = nt.send_post_request(self.addr, self.path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def clear_commands(self):
        payload = {"method": "clear_commands"}
        res = nt.send_post_request(self.addr, self.path, json=payload)
        if not res.status_code == 200:
            return {"status": "fail", "msg": "return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def upload_file(self, target, local_file, des_path):
        file_path, file_name = os.path.split(local_file)
        payload = {"method": "get_result", "data": "some data"}
        with open(local_file, 'rb') as f:
            file = {
                    "files": (file_name, f.read()),
                    "method": "upload_c",
                    "target": target,
                    "des_path": des_path
                    }
            encode_data = encode_multipart_formdata(file)
            file_data = encode_data[0]
            header = {"Content-Type": encode_data[1]}
            res = requests.post(self.addr+self.path, headers=header, data=file_data, json=payload)

        if not res.status_code == 201:
            return {"status":"fail", "msg":"return code:{}".format(res.status_code)}
        body = json.loads(res.text)
        return body

    def download_file(self, file_path, local_path):
        """
        通用下载方法，下载文件
        Download from: https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
        :param file_path:
        :param local_path:
        :param target:
        :return:
        """

        file_dir, file_name = os.path.split(local_path)
        # NOTE the stream=True parameter below
        file = {
            "files": ("my_name", "x"),
            "method": "download",
            "des_path": file_path
        }
        encode_data = encode_multipart_formdata(file)
        file_data = encode_data[0]
        header = {"Content-Type": encode_data[1]}

        try:
            with requests.post(self.addr + self.path, headers=header, data=file_data, stream=True) as r:
                r.raise_for_status()
                file_dir, file_name = os.path.split(local_path)
                os.makedirs(file_dir)
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        # if chunk:
                        f.write(chunk)
        except Exception as e:
            log.error("Down load File Fail:{}".format(e))
            return "failed"
        return local_path

    def download_command_file(self, cmd_id, local_path):
        """
        通用下载方法，下载文件
        Download from: https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
        :param file_path:
        :param local_path:
        :param target:
        :param cmd_id:
        :return:
        """

        file, ext = os.path.splitext(local_path)
        if not ext == ".zip":
            log.error("{} 必须以.zip结尾".format(local_path))
            return ""

        # NOTE the stream=True parameter below
        file = {
            "files": ("my_name", "x"),
            "method": "download_c",
            "target": "",
            "cmd_id": cmd_id
        }
        encode_data = encode_multipart_formdata(file)
        file_data = encode_data[0]
        header = {"Content-Type": encode_data[1]}

        try:
            with requests.post(self.addr + self.path, headers=header, data=file_data, stream=True) as r:
                r.raise_for_status()
                file_dir, file_name = os.path.split(local_path)
                os.makedirs(file_dir) if not os.path.exists(file_dir) else None
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        # if chunk:
                        f.write(chunk)
        except Exception as e:
            log.error("Down load File Fail:{}".format(e))
            return "failed"
        return local_path

    def cli(self, argv: []):
        """
        客户端接口程序
        """
        log.info("Argv: {}".format(','.join(argv)))
        if len(argv) == 2:
            show_cli_help()
            return 0

        if len(argv) == 3:
            if argv[2] == "env":
                return self.get_env()
            elif argv[2].startswith('1'):
                return self.get_result(argv[2])
            elif argv[2] == "clear":
                return self.clear_commands()
            else:
                return self.get_targets(argv[2])

        if len(argv) == 4:
            if argv[2] == "drop":
                return self.drop_command(argv[3])

        if len(argv) == 5 and argv[3] == 'cmd':     # poster master|slave|role cmd|fcmd|ufile|dfile command_args
            return self.put_command('cmd', argv[2], argv[4])

        if len(argv) == 5 and argv[3] == 'ufile_a':     # poster role ufile_a|cfile command_args
            return self.put_command('ufile_a', argv[2], argv[4])
        if len(argv) == 5 and argv[3] == 'cfile':     # poster role ufile_a|cfile command_args
            return self.put_command('ufile_a', argv[2], argv[4])

        if len(argv) == 5 and argv[2] == 'dfile':     # poster dfile cmd_id local_file.zip
            return self.download_command_file(argv[3], argv[4])

        if len(argv) == 6:     # poster role ufile|sfile local_file dest_file
            return self.upload_file(argv[2], argv[4], argv[5])

        print("无法解析的参数：{}".format(argv))
        show_cli_help()
        return -1


if __name__ == "__main__":
    poster = Poster()
    # res = poster.get_env()
    # print(res)
    res = poster.put_command('cmd', 'role1', "sleep 2")
    print(res)
    id = res["cmd_id"]
    res = poster.get_result(id)

    # res = poster.upload_file('role1','/Users/mawentao/PycharmProjects/data-test/dt4test/src/dt4test/webui/utils/temp_up/1.sh', '/Users/mawentao/PycharmProjects/data-test/dt4test/src/dt4test/webui/utils/temp_down/s.sh')
    # print(res)

    # res = poster.put_command('ufile_a', 'role1', "/Users/mawentao/PycharmProjects/data-test/dt4test/src/dt4test/webui/utils/temp_up/1.sh")
    # print(res)

    # res = poster.download_command_file("1115205907_811", "/Users/mawentao/PycharmProjects/data-test/dt4test/src/dt4test/webui/utils/temp_down/x.zip")
    # print(res)
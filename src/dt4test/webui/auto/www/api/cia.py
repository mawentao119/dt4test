# -*- coding: utf-8 -*-
__auther__ = "mawentao119@gmail.com"

import random
import shutil

"""
Recieve commands and dispatch commands to roles
From: dt poster [target] command 
To: [target]
"""

from flask import current_app, request, send_file, make_response
from flask_restful import Resource, reqparse
import os
import time
from urllib.parse import quote
from utils.mylogger import getlogger


class Cia(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('method', type=str)
        self.parser.add_argument('group_roles', type=str)
        self.parser.add_argument('ip', type=str)
        self.parser.add_argument('role_ids', type=str)
        self.parser.add_argument('info', type=str)
        self.parser.add_argument('cmd_type', type=str)
        self.parser.add_argument('target', type=str)
        self.parser.add_argument('cmd_arg', type=str)
        self.parser.add_argument('sub_id', type=str)
        self.parser.add_argument('role_id', type=str)
        self.parser.add_argument('cmd_id', type=str)
        self.parser.add_argument('ret_code', type=str)
        self.parser.add_argument('out', type=str)
        self.parser.add_argument('err', type=str)

        self.log = getlogger(__name__)
        self.app = current_app._get_current_object()
        
        self.topology = self.app.config["TOPOLOGY"]
        self.commands = self.app.config["COMMANDS"]
        self.subcommands = self.app.config["SUBCOMMANDS"]
        self.command_types = self.app.config["COMMAND_TYPES"]
        self.interval = self.app.config["AGENT_INTERVAL"]

    def post(self):

        # For normal requests
        args = request.form.to_dict()

        # For file upload and download
        if not args.get("method", None):
            args = self.parser.parse_args()

        method = args["method"].lower()

        if method == "register":
            return self.register(args)
        elif method == "get_env":
            return self.get_env(args)
        elif method == "get_target" or method == "get_role":
            return self.get_targets(args)
        elif method == "get_command":
            return self.get_command(args)
        elif method == "put_command":
            return self.put_command(args)
        elif method == "get_result":
            return self.get_result(args)
        elif method == "put_result":
            return self.put_result(args)
        elif method == "drop_command" or method == "delete_command" or method == "rm_command":
            return self.drop_command(args)
        elif method == "clear_commands":
            return self.clear_commands(args)
        elif method == "get_command_list":
            return self.get_command_list(args)

        elif method == "ufile" or method == "upload":       # upload file to target
            file = request.files.to_dict()['files']
            return self.__upload(file, args), 201
        elif method == "ufile_c" or method == "upload_c":       # upload file to target
            file = request.files.to_dict()['files']
            return self.__upload_c(file, args), 201
        elif method == "dfile" or method == "download":    # download normal file
            return self.__download(args)
        elif method == "ufile_a" or method == "upload_a":   # agent upload file for command
            file = request.files.to_dict()['files']
            return self.__upload_a(file, args), 201
        elif method == "dfile_a" or method == "download_a":  # agent download file for command
            return self.__download_a(args)
        elif method == "dfile_c" or method == "download_c":  # agent download file for command
            return self.__download_c(args)

        else:
            self.log.error("不支持的操作 'method' :{}".format(args['method']))
            return {"status": "fail", "msg": "不支持的操作 'method' :{}".format(args['method'])}

    def register(self, args):
        roles = args["group_roles"].split(',')
        ip = args["ip"]
        role_ids = []
        for item in roles:
            tmp = item.split(':')
            role = tmp[0]
            if len(tmp) > 1 :
                group = tmp[1]
            else:
                group = "unknown"
            role_id = self._add_to_topology(role, group, ip)
            role_ids.append(role_id)
        ids = ",".join(role_ids)
        self.log.info("注册成功 {}:{}".format(ip,ids))
        return {"status": "success", "msg": "OK", "role_ids": role_ids}

    def _add_to_topology(self, role, group, ip):
        """
        增加角色，topology 当前考虑一台机器上可以起多个role（docker情况），一个client可以归属多个role（1机多组件情况）
        :param role:
        :param group:
        :param ip:
        :return:
        """
        rnd = random.randint(100, 999)
        role_id = role + "_" + ip + "_" + str(1000 + rnd)
        new_role = {"role_id": role_id, "ip": ip, "role": role, "group": group, "report": 0.0, "is_alive": True}

        roles = self.topology.get(role, None)
        if roles:
            # for item in roles:
            #     count += 1
            #     if item["ip"] == ip:
            #         role_id = item["role_id"]
            #         item["is_alive"] = True
            #         self.log.info("角色ip存在:{}".format(ip))
            #         return role_id

            roles.append(new_role)
            self.log.info("追加新角色: {}:{}".format(role_id, ip))
            return role_id

        self.topology[role] = [new_role]
        self.log.info("创建新角色: {}:{}".format(role_id, ip))
        return role_id

    def _get_targets(self, target):
        """
        取得 target 所指代的 role ids
        :param target:
        :return:
        """
        role = target
        index = -1
        if target.find('[') != -1:
            role, left = target.split('[')
            index = int(left.split(']')[0])

        role_ids = []
        dead_roles = []
        roles = self.topology.get(role, [])
        if len(roles) > 0:
            now = time.time()
            timeout = 2 * self.interval
            for item in roles:
                if now - item["report"] < timeout:
                    role_ids.append(item["role_id"])
                else:
                    self.log.warn("超时的角色:{}".format(item["role_id"]))
                    item["is_alive"] = False
                    dead_roles.append(item)

            # 删除超时的角色
            for i in dead_roles:
                self.log.info("删除超时角色: {}".format(i))
                roles.remove(i)

        if index >= 0:
            if len(role_ids) > index:
                return [role_ids[index]]
            else:
                return []
        else:
            return role_ids

    def _gen_command_id(self):
        pre_fix = time.strftime("%m%d%H%M%S_", time.localtime(time.time()))
        cmd_id = random.randint(101, 999)
        return pre_fix + str(cmd_id)

    def _add_command(self, target, num_jobs, cmd_type, cmd_arg):
        """
        需要带 拆分的任务数 避免删除的维护
        :param target:
        :param num_jobs:
        :param cmd_type:
        :param cmd_arg:
        :return:
        """
        cmd_id = self._gen_command_id()
        cmd = {"target": target,
               "cmd_type":cmd_type,
               "cmd_arg": cmd_arg,
               "num_jobs": num_jobs,
               "time": time.time(),
               "last_report": 0.0,
               "result": []}
        self.commands[cmd_id] = cmd
        self.log.info("Add Cmd: {}:{}".format(cmd_id, cmd))
        return cmd_id

    def _drop_command(self, cmd_id):
        cmd = self.commands.get(cmd_id)
        if cmd:
            self.commands.pop(cmd)

        return True

    def _add_subcommand(self, role_id, cmd):
        role_cmds = self.subcommands.get(role_id, None)
        if role_cmds:
            role_cmds.append(cmd)
            self.log.info("ADD Subcmd: {}:{}".format(cmd["sub_id"], role_id))
        else:
            self.subcommands[role_id] = [cmd]

        return role_id

    def _drop_subcommand(self, cmd_id):
        """
        删除某个任务的运行，对于没有下发的子任务
        :param cmd_id:
        :return:
        """
        for role_id in self.subcommands:
            cmds = self.commands.get(role_id)
            deletes = []
            for c in cmds:
                if c["cmd_id"] == cmd_id:
                    deletes.append(c)
            for d in deletes:
                self.log.info("Delete subcommand: {}".format(d["sub_id"]))
                cmds.remove(d)

        return True

    def _get_subcommand(self, role_ids):
        cmds = []
        for rid in role_ids:
            if self.subcommands.get(rid, None):
                role_jobs = self.subcommands.pop(rid)
                for job in role_jobs:
                    cmds.append(job)

        return cmds

    def get_targets(self, args):
        """
        返回操作目标的id列表
        return: [id1,id2]
        """
        role_ids = self._get_targets(args["target"])
        if len(role_ids) > 0:
            ids = ','.join(role_ids)
            return {"status": "success", "msg": "OK", "role_ids": ids}
        else:
            return {"status": "fail", "msg": "Cannot find role: {}".format(args["target"]), "role_ids": ""}

    def drop_command(self, args):
        cmd_id = args["cmd_id"]
        self.log.info("删除command：{}".format(cmd_id))
        result1 = self._drop_command(cmd_id)
        result2 = self._drop_subcommand(cmd_id)
        if result1 and result2:
            return {"status": "success", "msg": "drop command {} OK".format(cmd_id)}
        else:
            return {"status": "fail", "msg": "drop command {} fail, Please see log".format(cmd_id)}

    def clear_commands(self, args):
        self.log.info("清除Commands")
        self.commands.clear()
        return {"status": "success", "msg": "Clear commands ok", "data": self.commands}

    def get_command_list(self, args):
        cmds = []
        for cmd in self.commands:
            item = {"cmd_id": cmd["cmd_id"], "target": cmd["target"], "cmd_arg": cmd["cmd_arg"]}
            cmds.append(item)

        return {"status": "success", "msg": "get commands ok", "data": cmds}

    def put_command(self, args):
        """
        Client 提交的任务请求
        :param args:
        :return:
        """
        target = args["target"]
        cmd_type = args["cmd_type"]
        cmd_arg = args["cmd_arg"]

        role_ids = self._get_targets(target)
        if len(role_ids) == 0:
            return {"status": "fail", "msg": "Cannot find role", "cmd_id": ""}

        if not cmd_type in self.command_types:
            return {"status": "fail", "msg": "cmd_type no in:{}".format(self.command_types), "cmd_id": ""}

        num_jobs = len(role_ids)

        cmd_id = self._add_command(target, num_jobs, cmd_type, cmd_arg)

        for idx, rd in enumerate(role_ids):
            sub_id = cmd_id + "_" + str(idx)
            sub_cmd = {"sub_id": sub_id, "cmd_type": cmd_type, "cmd_arg": cmd_arg, "cmd_id": cmd_id, "role_id": rd}
            self._add_subcommand(rd, sub_cmd)

        return {"status": "success", "msg": "Put command success", "cmd_id": cmd_id}

    def get_command(self, args):
        """
        Agent 的心跳，通过心跳返回带回需要执行的命令，可以携带 info 参数，后续扩展
        :param args:
        :return:
        """
        ids = args["role_ids"].split(',')

        for rd in ids:
            self.update_role_status(rd)

        cmds = self._get_subcommand(ids)

        return {"status": "success", "msg": "Get command success", "cmds": cmds}

    def update_role_status(self, role_id):
        """
        更新role的status
        :param role_id: role_xx.xx.xx.xx_index
        :return:
        """
        role = role_id.split('_')[0]
        roles = self.topology.get(role)
        if roles:
            for r in roles:
                if r["role_id"] == role_id:
                    r["report"] = time.time()
                    r["is_alive"] = True
                    self.log.debug("Agent更新状态 {}".format(role_id))
                    break
        else:
            self.log.error("Agent更新状态，找不到角色: {}".format(role_id))

    def put_result(self, args):
        """
        Agent 上报任务运行结果
        :param args:
        :return:
        """
        sub_id = args["sub_id"]
        cmd_id = args["cmd_id"]
        role_id = args["role_id"]
        ret_code = args["ret_code"]
        out = args["out"]
        err = args["err"]

        result = { "sub_id": sub_id,
                   "role_id": role_id,
                   "ret_code": ret_code,
                   "out": out,
                   "err": err,
                   "time": time.time()}

        if self._put_result(cmd_id, result):
            return {"status": "success", "msg": "Put result success"}
        else:
            return {"status": "fail", "msg": "Put result failed"}

    def _put_result(self, cmd_id, result):
        cmd = self.commands.get(cmd_id, None)
        if cmd:
            cmd["result"].append(result)
            cmd["last_report"] = result["time"]
            self.log.info("Get Result: {}:{}".format(result["sub_id"], result["role_id"]))
            return True
        else:
            self.log.error("找不到任务: {}".format(cmd_id))
            return False

    def get_result(self, args):
        """
        返回任务结果，暂时实现实时返回，后续支持 timeout 的服务端重试
        :param args:
        :return:
        """
        if args.get("timeout", None):
            return {"status": "fail", "msg": "Not support timeout now."}

        cmd_id = args["cmd_id"]
        if self.commands.get(cmd_id):
            cmd = self.commands.get(cmd_id)
            if cmd["num_jobs"] == len(cmd["result"]):     # Finished then pop otherwise not pop.
                cmd = self.commands.pop(cmd_id)
            return {"status": "success", "msg": "get result success", "result": cmd["result"]}
        else:
            return {"status": "fail", "msg": "cmd_id: {} is not found".format(cmd_id)}

    def _get_result(self, cmd_id):

        cmd = self.commands.pop(cmd_id)
        return cmd["result"]

    def get_env(self, args):
        return {"status": "success", "msg": "get env success", "data": self.topology}

    def write_conf(self, args):
        """
        TODO: write config file .ini
        :param args:
        :return:
        """
        return {"status": "success", "msg": "get env success","data":self.topology}

    def __upload(self, file, args):
        des_path = args["des_path"]
        result = {"status": "success", "msg": "成功：上传文件."}
        user_path = des_path + '/' + file.filename
        os.makedirs(des_path) if not os.path.exists(des_path) else None
        if not os.path.exists(user_path):
            file.save(user_path)
        else:
            result["status"] = "fail"
            result["msg"] = "文件已存在."
        self.app.config['DB'].insert_loginfo(self.app.config['USER_NAME'], 'file', 'upload', user_path)

        return result

    def __upload_c(self,file, args):
        result = {"status": "success", "msg": "", "cmd_id": "", "file":""}

        target = args["target"]
        cmd_type = "dfile_a"
        cmd_arg = args["des_path"]

        role_ids = self._get_targets(target)
        if len(role_ids) == 0:
            return {"status": "fail", "msg": "Cannot find role", "cmd_id": ""}

        if not cmd_type in self.command_types:
            return {"status": "fail", "msg": "cmd_type no in:{}".format(self.command_types), "cmd_id": ""}

        num_jobs = len(role_ids)

        cmd_id = self._add_command(target, num_jobs, cmd_type, cmd_arg)

        file_dir = '/tmp/'+cmd_id
        file_name = file_dir + "/" + file.filename
        os.mkdir(file_dir)

        if not os.path.exists(file_name):
            file.save(file_name)
        else:
            result["status"] = "fail"
            result["msg"] = "文件已存在."
            self._drop_command(cmd_id)

        self.app.config['DB'].insert_loginfo(self.app.config['USER_NAME'], 'file', 'upload', file_name)

        for idx, rd in enumerate(role_ids):
            sub_id = cmd_id + "_" + str(idx)
            sub_cmd = {"sub_id": sub_id, "cmd_type": cmd_type, "cmd_arg": cmd_arg, "cmd_id": cmd_id, "role_id": rd}
            self._add_subcommand(rd, sub_cmd)

        result["cmd_id"] = cmd_id
        result["file"] = file_name

        return result

    def __upload_a(self, file, args):
        """
        Agent upload file of command
        :param file:
        :param args:
        :return:
        """
        result = {"status": "success", "msg": "", "cmd_id": "", "file": ""}

        role_id = args["target"]
        cmd_id = args["des_path"]

        self.log.info("Agent {}: Upload file , cmd_id:{} ".format(role_id, cmd_id))

        file_dir = '/tmp/'+cmd_id
        file_name = file_dir + "/" + file.filename
        os.mkdir(file_dir)

        if not os.path.exists(file_name):
            file.save(file_name)
        else:
            result["status"] = "fail"
            result["msg"] = "文件已存在."

        self.app.config['DB'].insert_loginfo(self.app.config['USER_NAME'], 'file', 'upload', file_name)

        result["cmd_id"] = cmd_id
        result["file"] = file_name

        return result

    def __download(self, args):
        # charis added :
        user_path = args['des_path']
        self.log.info("下载文件请求路径:" + user_path)
        self.app.config['DB'].insert_loginfo(self.app.config['USER_NAME'], 'file', 'download', user_path)
        return self.__sendfile(user_path)

    def __download_a(self, args):
        """
        Agent down load file for command
        :param args:
        :return:
        """
        cmd_id = args["des_path"]
        role_id = args["target"]
        self.log.info("Agent: {} Download file cmd_id: {}".format(role_id, cmd_id))
        files = os.listdir("/tmp/"+cmd_id)
        if len(files) == 0:
            self.log.error("Agent找不到下载文件:cmd_id {}".format(cmd_id))
        file_name = "/tmp/" + cmd_id + "/" + files[0]
        return self.__sendfile(file_name)

    def __download_c(self, args):
        """
        Client down load file for command
        :param args:
        :return:
        """
        cmd_id = args["cmd_id"]
        self.log.info("Client: Download file cmd_id: {}".format(cmd_id))
        files = os.listdir("/tmp/"+cmd_id)
        if len(files) == 0:
            self.log.error("找不到下载文件:cmd_id {}".format(cmd_id))

        file_name = "/tmp/" + cmd_id
        shutil.make_archive(file_name, 'zip', root_dir='/tmp', base_dir=cmd_id)
        self.log.info("打包文件：{}".format(file_name + ".zip"))
        return self.__sendfile(file_name + ".zip")

    def __sendfile(self, f):
        response = make_response(send_file(f))
        basename = os.path.basename(f)
        response.headers["Content-Disposition"] = \
            "attachment;" \
            "filename*=UTF-8''{utf_filename}".format(
                utf_filename=quote(basename.encode('utf-8'))
            )
        return response


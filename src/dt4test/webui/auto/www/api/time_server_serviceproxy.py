# -*- coding: utf-8 -*-
__auther__ = "mawentao119@gmail.com"

import logging
import random
import shutil

"""
Scheduler Tester Interface for Data perform
From: dt sc [target] command 
To: [target]
"""

from flask import current_app, request
from flask_restful import Resource, reqparse
from utils.mylogger import getlogger

log = getlogger(__name__)

class ServiceProxy(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('method', type=str)
        self.parser.add_argument('max_tasks', type=str)
        self.parser.add_argument('max_insts', type=str)
        self.parser.add_argument('tasks_wanted', type=str)
        self.parser.add_argument('taskids', type=str)
        self.parser.add_argument('instids', type=str)
        self.parser.add_argument('insts_per_task', type=str)
        self.parser.add_argument('task_id', type=str)
        self.parser.add_argument('inst_id', type=str)
        self.parser.add_argument('clear_data', type=str)
        self.parser.add_argument('service_dir', type=str)
        self.parser.add_argument('service_file', type=str)
        self.parser.add_argument('interval', type=str)

        self.log = getlogger(__name__)
        self.app = current_app._get_current_object()
        
        self.SV = self.app.config["SV"]

    def post(self):

        # For normal requests
        args = request.form.to_dict()

        # For file upload and download
        if not args.get("method", None):
            args = self.parser.parse_args()

        method = args.get("method", None)
        if not method:
            return {"status": "fail", "msg": "参数缺少 'method' "}

        method = args["method"].lower()

        if method == "add_one_task" or method== "update_one_task":
            return self.add_one_task(args)
        elif method == "add_one_inst" or method == "update_one_inst":
            return self.add_one_inst(args)
        elif method == "update_data":
            return self.update_data(args)
        elif method == "init_service":
            return self.init_service(args)
        elif method == "clear_data":
            return self.clear_data()
        elif method == "clear_tasks":
            return self.clear_tasks()
        elif method == "clear_insts":
            return self.clear_insts()
        elif method == "del_task" or method == "remove_task":
            return self.remove_task(args)
        elif method == "del_inst" or method == "remove_inst":
            return self.remove_inst(args)
        elif method == "get_update_interval":
            return self.get_update_interval()
        elif method == "set_update_interval":
            return self.set_update_interval(args)
        elif method == "get_need_do":
            return self.get_need_do()
        elif method == "start_update":
            return self.start_update()
        elif method == "stop_update":
            return self.stop_update()

        else:
            self.log.error("不支持的操作 'method' :{}".format(args['method']))
            return {"status": "fail", "msg": "不支持的操作 'method' :{}".format(args['method'])}

    def add_one_task(self, args):
        task_id = args.get("task_id", None)
        insts_per_task = args.get("insts_per_task", None)

        if not task_id:
            log.error("缺少参数：task_id ")
            return {"status": "fail", "msg": "缺少参数：task_id"}

        if self.SV.update_one_task(task_id):
            return {"status": "success", "msg": "OK"}
        
        return {"status": "fail", "msg": "Service 执行失败"}
    
    def add_one_inst(self, args):
        inst_id = args.get("inst_id", None)

        if not inst_id:
            log.error("缺少参数：inst_id ")
            return {"status": "fail", "msg": "缺少参数：inst_id"}

        task_added, inst_added = self.SV.update_one_inst(inst_id)
        return {"status": "success", "msg": "OK", "tasks_added": task_added, "inst_added": inst_added}

    def update_data(self, args):
        if self.SV.update_data():
            return {"status": "success", "msg": "OK"}
        else:
            return {"status": "fail", "msg": "Service 执行失败"}

    def init_service(self, args):
        service_dir = args.get("service_dir", None)
        service_file = args.get("service_file", None)
        clear_data = args.get("clear_data", False)

        inst = None
        info = "unknown"
        if (not service_dir) and (not service_file):
            inst, info = self.SV.init_service()
        if (not service_dir) and service_file:
            inst, info = self.SV.init_service(service_file=service_file, clear_data=clear_data)
        if service_dir and service_file:
            inst, info = self.SV.init_service(service_dir, service_file, clear_data=clear_data)

        if not inst:
            return {"status": "fail", "msg": info}
        else:
            return {"status": "success", "msg": info}

    def remove_task(self, args):
        task_id = args("task_id", None)
        if not task_id:
            return {"status": "fail", "msg": "缺少参数 task_id"}
        if self.SV.remove_task(task_id):
            return {"status": "success", "msg": task_id}
        else:
            return {"status": "fail", "msg": "删除失败，请查看日志"}

    def remove_inst(self, args):
        inst_id = args("inst_id", None)
        if not inst_id:
            return {"status": "fail", "msg": "缺少参数 inst_id"}
        if self.SV.remove_inst(inst_id):
            return {"status": "success", "msg": inst_id}
        else:
            return {"status": "fail", "msg": "删除失败，请查看日志"}

    def clear_data(self):
        self.SV.clear_data()
        return {"status": "success", "msg": "OK"}

    def clear_tasks(self):
        self.SV.clear_tasks()
        return {"status": "success", "msg": "OK"}

    def clear_insts(self):
        self.SV.clear_insts()
        return {"status": "success", "msg": "OK"}

    def get_need_do(self):
        info = self.SV.get_need_do()
        return {"status": "success", "msg": "{}".format(info)}

    def get_update_interval(self):
        info = self.SV.get_update_interval()
        return {"status": "success", "msg": "{}".format(info)}

    def set_update_interval(self, args):
        interval = args["interval"]
        info = self.SV.set_update_interval(interval)
        return {"status": "success", "msg": "{}".format(info)}

    def stop_update(self):
        info = self.SV.stop_update()
        return {"status": "success", "msg": "{}".format(info)}

    def start_update(self):
        ok = self.SV.start_update()
        if ok:
            return {"status": "success", "msg": "{}".format(ok)}
        else:
            return {"status": "fail", "msg": "{}:update is running,请稍后重试".format(ok)}



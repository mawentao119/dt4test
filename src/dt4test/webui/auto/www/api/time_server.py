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

class TimeServer(Resource):
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

        self.app = current_app._get_current_object()
        
        self.SD = self.app.config["SD"]

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

        if method == "get_start_time":
            return self.get_start_time()
        elif method == "del_task" or method == "remove_task":
            return self.remove_task(args)
        elif method == "del_inst" or method == "remove_inst":
            return self.remove_inst(args)
        elif method == "get_insts_bytes":
            return self.get_insts_bytes()
        elif method == "get_tasks_bytes":
            return self.get_tasks_bytes()
        elif method == "get_task_record":
            return self.get_task_record(args)

        else:
            log.error("不支持的操作 'method' :{}".format(args['method']))
            return {"status": "fail", "msg": "不支持的操作 'method' :{}".format(args['method'])}

    def get_start_time(self):
        st = self.SD.get_start_time()
        return {"status": "success", "msg": "OK","starttime": st}

    def remove_task(self, args):
        task_id = args.get("task_id", None)
        if not task_id:
            return {"status": "fail", "msg": "缺少参数 task_id"}

        res = self.SD.remove_task(task_id)
        return {"status": "success", "msg": "{}".format(res)}

    def remove_inst(self, args):
        inst_id = args.get("inst_id", None)
        if not inst_id:
            return {"status": "fail", "msg": "缺少参数 inst_id"}

        res = self.SD.remove_inst(inst_id)
        return {"status": "success", "msg": "{}".format(res)}

    def clear_tasks(self):
        self.SD.clear_tasks()
        return {"status": "success", "msg": "OK"}

    def clear_insts(self):
        self.SD.clear_insts()
        return {"status": "success", "msg": "OK"}

    def get_insts_bytes(self):
        size = self.SD.get_insts_bytes()
        return {"status": "success", "msg": size}

    def get_tasks_bytes(self):
        size = self.SD.get_tasks_bytes()
        return {"status": "success", "msg": size}

    def get_task_record(self, args):
        task_id = args.get("task_id", None)
        if not task_id :
            log.error("缺少参数：task_id ")
            return {"status": "fail", "msg": "缺少参数：task_id "}
        records = self.SD.get_task_record(task_id)
        return {"status": "success", "msg": "get_task_records","data": records}


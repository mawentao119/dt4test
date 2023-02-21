# -*- coding: utf-8 -*-
__auther__ = "mawentao119@gmail.com"

"""
Check Rules of time_server
From: dt sc 
To: [target]
"""

from flask import current_app, request
from flask_restful import Resource, reqparse
from utils.mylogger import getlogger


class TimeServerCheckRule(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('method', type=str)
        self.parser.add_argument('rule_dir', type=str)
        self.parser.add_argument('rule_name', type=str)
        self.parser.add_argument('rule_file', type=str)
        self.parser.add_argument('interval', type=str)

        self.log = getlogger(__name__)
        self.app = current_app._get_current_object()
        
        self.CR = self.app.config["CR"]

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

        if method == "update_rule" or method == "update_rules":
            return self.update_rules(args)
        elif method == "add_one_rule":
            return self.add_one_rule(args)
        elif method == "remove_one_rule":
            return self.remove_one_rule(args)
        elif method == "run_one_rule" or method == "check_one_rule":
            return self.run_one_rule(args)
        elif method == "run_all_rule" or method == "check_all_rule":
            return self.run_all_rule()
        elif method == "get_all_rule" or method == "get_all_rules":
            return self.get_all_rule()
        elif method == "get_check_interval":
            return self.get_check_interval()
        elif method == "set_check_interval":
            return self.set_check_interval(args)
        elif method == "get_need_do":
            return self.get_need_do()
        elif method == "stop_do_check":
            return self.stop_do_check()
        elif method == "start_do_check":
            return self.start_do_check()
        elif method == "clear_mistakes":
            return self.clear_mistakes()
        elif method == "clear_rule_records":
            return self.clear_rule_records()
        elif method == "clear_rules":
            return self.clear_rules()

        elif method == "get_report":
            return self.get_report()
        elif method == "get_rule_report":
            return self.get_rule_report(args)

        else:
            self.log.error("不支持的操作 'method' :{}".format(args['method']))
            return {"status": "fail", "msg": "不支持的操作 'method' :{}".format(args['method'])}

    def update_rules(self, args):
        rule_dir = args.get("rule_dir", None)
        if not rule_dir:
            num, info = self.CR.update_rules()
        else:
            num, info = self.CR.update_rules(rule_dir)
        return {"status": "success", "num": num, "info":info}

    def add_one_rule(self, args):
        rule_dir = args.get("rule_dir", None)
        rule_file = args.get("rule_file", None)

        if not rule_dir or not rule_file:
            return {"status": "fail", "msg": "缺少参数 rule_dir|rule_file"}

        num, info = self.CR.add_one_rule(rule_file, rule_dir)
        return {"status": "success", "msg": "{}:{}".format(num, info)}

    def remove_one_rule(self, args):
        rule_name = args["rule_name"]
        num, info = self.CR.remove_one_rule(rule_name)
        return {"status": "success", "msg": "{}:{}".format(num, info)}

    def run_one_rule(self, args):
        rule_name = args["rule_name"]
        report = self.CR.run_one_rule(rule_name)
        return {"status": "success", "msg": "{}".format(report)}

    def run_all_rule(self):
        report = self.CR.run_all_rule()
        return {"status": "success", "msg": "{}".format(report)}

    def get_all_rule(self):
        rule_names = self.CR.get_all_rule()
        return {"status": "success", "msg": "{}".format(rule_names)}

    def get_report(self):
        info = self.CR.get_report()
        return {"status": "success", "msg": "{}".format(info)}

    def get_rule_report(self, args):
        rule_name = args["rule_name"]
        report = self.CR.get_rule_report(rule_name)
        return {"status": "success", "msg": "{}".format(report)}

    def get_check_interval(self):
        info = self.CR.get_check_interval()
        return {"status": "success", "msg": "{}".format(info)}

    def set_check_interval(self, args):
        interval = args["interval"]
        info = self.CR.set_check_interval(interval)
        return {"status": "success", "msg": "{}".format(info)}

    def get_need_do(self):
        info = self.CR.get_need_do()
        return {"status": "success", "msg": "{}".format(info)}

    def stop_do_check(self):
        info = self.CR.stop_do_check()
        return {"status": "success", "msg": "{}".format(info)}

    def start_do_check(self):
        ok = self.CR.start_do_check()
        if ok:
            return {"status": "success", "msg": "{}".format(ok)}
        else:
            return {"status": "fail", "msg": "{}: check is running，请稍后再试".format(ok)}

    def clear_mistakes(self):
        info = self.CR.clear_mistakes()
        return {"status": "success", "msg": "{}".format(info)}

    def clear_rule_records(self):
        info = self.CR.clear_rule_records()
        return {"status": "success", "msg": "{}".format(info)}

    def clear_rules(self):
        info = self.CR.clear_rules()
        return {"status": "success", "msg": "{}".format(info)}
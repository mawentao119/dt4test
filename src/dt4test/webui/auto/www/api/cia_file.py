# -*- coding: utf-8 -*-

__author__ = "mawentao119@gmail.com"


"""
Deal with request of file transfering command in cia systems
"""

import os
from flask import current_app, request, send_file, make_response
from flask_restful import Resource

from urllib.parse import quote
from utils.mylogger import getlogger


class CiaFile(Resource):
    """
    Upload file and Download file
    This class is replaced by Cia , Should be deleted.
    # TODO : Delete never used func
    """
    def __init__(self):
        self.app = current_app._get_current_object()
        self.log = getlogger(__name__)

    def post(self):
        args = request.form.to_dict()
        self.log.info("Post:args:{}".format(args))
        method = args["method"].lower()
        if method == "ufile" or method == "upload":
            file = request.files.to_dict()['files']
            return self.__upload(file, args['des_path']), 201
        elif method == "dfile" or method == "download":
            return self.__download(args)

    def __upload(self, file, des_path):
        result = {"status": "success", "msg": "成功：上传文件."}
        user_path = des_path + '/' + file.filename
        if not os.path.exists(user_path):
            file.save(user_path)
        else:
            result["status"] = "fail"
            result["msg"] = "文件已存在."
        self.app.config['DB'].insert_loginfo(self.app.config['USER_NAME'], 'file', 'upload', user_path)

        return result

    def __download(self, args):
        # charis added :
        user_path = args['des_path']
        self.log.info("下载文件请求路径:" + user_path)
        self.app.config['DB'].insert_loginfo(self.app.config['USER_NAME'], 'file', 'download', user_path)
        return self.__sendfile(user_path)

    def __sendfile(self, f):
        response = make_response(send_file(f))
        basename = os.path.basename(f)
        response.headers["Content-Disposition"] = \
            "attachment;" \
            "filename*=UTF-8''{utf_filename}".format(
                utf_filename=quote(basename.encode('utf-8'))
            )
        return response

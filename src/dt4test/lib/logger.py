import logging
import os
from datetime import datetime, date

from .helper import Helper

"""Log Module of Project"""
loggers = {}


class Logger(Helper):
    """
    可以通过传入log文件名，指定log文件，如果没有 ${PROJECT_DIR}环境变量，则放在 /tmp 目录下面
    """
    def __init__(self, logfile_path=""):
        self.log_name = "dt4test.log"
        if logfile_path:
            self.logfile = logfile_path    # 如果构造函数提供文件名，则用构造函数的logfilename
        else:
            log_dir = "/tmp"
            if os.environ.get("PROJECT_DIR", None):     # 如果设置了环境变量，使用环境变量
                log_dir = os.path.join(os.environ["PROJECT_DIR"], "output")
                os.makedirs(log_dir) if not os.path.exists(log_dir) else None
            self.logfile = os.path.join(log_dir, self.log_name)

    def get_logfile(self):
        return self.logfile

    def get_logger(self, name=__name__):
        """
        | 统一log函数，log文件：${PROJECT_DIR}/output/dt4test.log
        | 如果没有配置 PROJECT_DIR 环境变量，则记录在/tmp/dt4test.log
        | :param name: 类名
        | :return: log配置
        | **Example:**
        | from dt4test import Logger
        | log = Logger().getl_logger(__name__)
        | log.info("some log info")
        """
        global loggers

        if loggers.get(name):
            return loggers.get(name)

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(self.logfile)
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.INFO)

        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(name)s %(levelname)s (%(funcName)s:%(lineno)s) %(message)s')
        f_format = logging.Formatter('%(asctime)s %(name)s %(levelname)s (%(funcName)s:%(lineno)s) %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # logger.addHandler(c_handler)
        logger.addHandler(f_handler)

        loggers[name] = logger

        return logger

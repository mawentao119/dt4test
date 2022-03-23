import logging
import os
from datetime import datetime, date

"""Log Module of Project"""
loggers = {}
def getlogger(name=__name__):
    global loggers

    if loggers.get(name):
        return loggers.get(name)

    log_name = "dt4test_ui.log"
    log_dir = "/tmp"
    if os.environ.get("PROJECT_DIR", None):  # 如果设置了环境变量，使用环境变量
        log_dir = os.path.join(os.environ["PROJECT_DIR"], "output")
        os.makedirs(log_dir) if not os.path.exists(log_dir) else None
    LogFile = os.path.join(log_dir, log_name)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(LogFile)
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(name)s %(levelname)s (%(funcName)s:%(lineno)s) %(message)s')
    f_format = logging.Formatter('%(asctime)s %(name)s %(levelname)s (%(funcName)s:%(lineno)s) %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    loggers[name] = logger

    return logger
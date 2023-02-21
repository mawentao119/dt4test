# -*- utf-8 -*-

###############################################################
# Test Scheduler system, backend checker
# __author__ = "mawentao119@gmail.com"
# __datetime__ = "2023-02-11 17:43:00"
###############################################################

import os
import sys
import inspect

from datetime import datetime

from .mylogger import getlogger

log = getlogger(__name__)


def get_time_now():
    """
    用来记录实例及task扫描归档时间，后续可能会用来评估耗时
    :return:
    """
    return datetime.now().strftime("%Y%m%d%H%M%S")

def load_single_module_from_path(path, py_file):
    """
   Import all modules from the given directory
   """
    is_mod_loaded = False

    # Check and fix the path
    if path[-1:] != '/':
        path += '/'

    # Get a list of files in the directory, if the directory exists
    if not os.path.exists(path):
        log.error("目录不存在:{}".format(path))
        return False

    # Add path to the system path
    sys.path.append(path)
    # Load all the files in path
    for f in os.listdir(path):
        # Ignore anything that isn't a .py file
        if f != py_file:
            log.warn("发现无关模块，忽略 {}".format(f))
            continue
        if len(f) > 3 and f[-3:] == '.py':
            modname = f[:-3]
            # Import the module
            __import__(modname, globals(), locals(), ['*'])
            is_mod_loaded = True

    return is_mod_loaded


def load_modules_from_path(path):
    """
   Import all modules from the given directory
   """

    loaded_mod = []

    # Check and fix the path
    if path[-1:] != '/':
        path += '/'

    # Get a list of files in the directory, if the directory exists
    if not os.path.exists(path):
        log.error("目录不存在：{}".format(path))
        return loaded_mod

    # Add path to the system path
    sys.path.append(path)
    # Load all the files in path
    for f in os.listdir(path):
        # Ignore anything that isn't a .py file
        if len(f) > 3 and f[-3:] == '.py':
            modname = f[:-3]
            # Import the module
            __import__(modname, globals(), locals(), ['*'])
            loaded_mod.append(modname)

    return loaded_mod


def load_class_from_name(class_dot_name):
    # Break apart fqcn to get module and classname
    paths = class_dot_name.split('.')
    modulename = '.'.join(paths[:-1])
    classname = paths[-1]
    # Import the module
    __import__(modulename, globals(), locals(), ['*'])
    # Get the class
    cls = getattr(sys.modules[modulename], classname)
    # Check cls
    if not inspect.isclass(cls):
        log.error("{} 不是一个类".format(class_dot_name))
        return None
    # Return class
    return cls


def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

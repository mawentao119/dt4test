#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dt4test import Logger

log = Logger().get_logger(__name__)

MODULE_NAME = 'myres'     # 这个是 dt myres 调用入口 TODO：修改模块名


def show_usage():
    """
    Resource的使用方法，可以通过 dt resource
    """
    print("myres : show this help ")
    print("myres run : run my fun ...")


class MyResource():      # TODO: 修改类名
    """
    My Resource
    """
    def __init__(self):
        print("Gog give me birth.")

    def cli(self, argv=[]):
        """
        有用于dt程序调用， 子任务成功返回 0 ，否则返回 非0 值

        | :param argv:  sys.argv
        | :return:  0 OR not 0
        """
        if len(argv) == 2:
            show_usage()
            return 0

        if argv[2] == 'run':
            self.my_fun()
            return 0

    def my_fun(self):
        """
        My supper weapon
        """
        log.info("Test my function ")
        print("Run my fun ...")


MODULE_INSTANCE = MyResource()       # TODO：检查类名是否一致

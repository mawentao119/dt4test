## Library for Basic functions ##
## Author: charisma
## Birthday: 2021-12-09
###################################

import os
import uuid
import random
import time

from .helper import Helper

from .logger import Logger

log = Logger().get_logger(__name__)

class Base(Helper):
    """
    基础的公共函数
    """
    def list_to_string(self, alist, split_char=','):
        """
        | 将list转化成一个字符串，以split_char分割
        | :param alist: list
        | :param split_char: split_char
        | :return: String

        | **Example** :
        | l2 = ['x', 1, 2, 'y']
        | s2 = list_to_string(l2, ':')
        | assert s2 == "x:1:2:y"
        """
        log.info("len(alist):{}, split_char:{}".format(len(alist), split_char))
        newlist = [str(x) for x in alist]
        return split_char.join(newlist)


    def get_uuid(self):
        """
        | Return uuid
        | :return: uuid
        """
        return str(uuid.uuid1())


    def get_a_random_item(self, alist):
        """
        | 选择list中的一个随机值
        | :param alist: list
        | :return: a member
        """
        return random.choice(alist)


    def gen_outputdir(self):
        """
        生成统一的输出目录
        """
        t = time.strftime("%Y%m%d%H%M%S", time.localtime())
        r = random.randint(100, 999)
        dir_name = "{}_{}".format(t, r)
        return dir_name



# -*- coding: utf-8 -*-

__author__ = "mawentao119@gmail.com"

"""

"""


class AutoBeatException(Exception):
    pass


class AutoBeatConfigException(AutoBeatException):
    pass


class AutoBeatExecutorTimeout(AutoBeatException):
    pass


class AutoBeatTaskTimeout(AutoBeatException):
    pass


class AutoBeatWebServerTimeout(AutoBeatException):
    pass


class AutoBeatSkipException(AutoBeatException):
    pass

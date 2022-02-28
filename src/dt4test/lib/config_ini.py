## Author: charisma
## Birthday: 2021-12-03
## Test under: py3.8
## ConfigParser 在 py2 和 py3 中是不一样的
###################################

import os
import configparser

from .helper import Helper
from .logger import Logger

log = Logger().get_logger()


class ConfigIni(Helper):
    """
    INI 格式的配置文件的处理，get ，set ，if exists
    """
    def set_item(self, filename, section, item, value):
        """
        | 设置配置文件中的配置项
        | filename: 配置文件名
        | section: ini 文件中的 section
        | item: section 下面的 配置项
        | value: 配置项的值
        |:return: 'ok' OR 'err'
        """
        if not os.path.exists(filename):
            log.error("找不到配置文件: {}".format(filename))
            return 'err'

        config = configparser.ConfigParser()
        config.read_file(open(filename))

        log.info("修改配置:file:{},section:{},item:{},value:{}".format(filename, section, item, value))
        if not config.has_section(section):
            log.info("没有此Section: {}".format(section))
            return 'err'
        config[section][item] = value
        with open(filename, 'w') as configfile:
            config.write(configfile)
        return 'ok'


    def get_item(self, filename, section, item):
        """
        | 取得配置项的值
        | filename: 配置文件名
        | section: INI 配置文件的section
        | item: Section下面的 配置项
        | :return: value OR '*err*'
        """
        if not os.path.exists(filename):
            log.error("找不到配置文件: {}".format(filename))
            return '*err*'

        config = configparser.ConfigParser()
        config.read_file(open(filename))

        log.info("取得配置:file:{},section:{},item:{}".format(filename, section, item))
        return config.get(section, item, fallback='')


    def item_exists(self, filename, section, item):
        """
        | 判断配置项是否存在
        | filename: 配置文件名
        | section: INI配置文件中的Section
        | item: 配置项
        | :return: True OR False
        """
        if not os.path.exists(filename):
            log.error("找不到配置文件: {}".format(filename))
            return '*err*'

        config = configparser.ConfigParser()
        config.read_file(open(filename))
        return config.has_option(section, item)


    def get_variables(self, filename):
        """
        | 取得所有配置项目的值
        | filename: 配置文件
        | :return: varialbles{"section.key":value}
        """
        config = configparser.ConfigParser()
        config.read_file(open(filename))

        variables = {}
        for section in config.sections():
            for key, value in config.items(section):
                var = "%s.%s" % (section, key)
                variables[var] = value
        return variables
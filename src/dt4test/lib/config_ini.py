## Author: charisma
## Birthday: 2021-12-03
## Test under: py3.8
## ConfigParser 在 py2 和 py3 中是不一样的
###################################

import os
import configparser

from .helper import Helper
from .logger import Logger

log = Logger().get_logger(__name__)


class ConfigIni(Helper):
    """
    INI 格式的配置文件的处理，get ，set ，if exists
    """
    def set_item(self, filename, section, item, value, add_new=False):
        """
        | 设置配置文件中的配置项
        | :param filename: 配置文件名
        | :param section: 配置段
        | :param item: 配置项
        | :param value: 配置值
        | :return: value OR ""
        """
        if not os.path.exists(filename):
            log.error("找不到配置文件: {}".format(filename))
            raise FileNotFoundError("{}".format(filename))

        config = configparser.ConfigParser()
        config.read_file(open(filename))

        log.info("修改配置:file:{},section:{},item:{},value:{}".format(filename, section, item, value))

        if not config.has_section(section) and not add_new:
            log.info("没有此Section: {}".format(section))
            raise ValueError("没有此Section: {}".format(section))

        if not config.has_section(section) and add_new:
            log.info("增加Section: {}".format(section))
            config.add_section(section)

        if not config.has_option(section, item) and not add_new:
            log.info("section:{} 没有此item: {}".format(section, item))
            raise ValueError("section:{} 没有此item: {}".format(section, item))

        if not config.has_option(section, item) and add_new:
            config[section][item] = value

        with open(filename, 'w') as configfile:
            config.write(configfile)
        return value


    def get_item(self, filename, section, item):
        """
        | 取得配置项的值
        | filename: 配置文件名
        | section: INI 配置文件的section
        | item: Section下面的 配置项
        | :return: value OR ''
        """
        if not os.path.exists(filename):
            log.error("找不到配置文件: {}".format(filename))
            raise FileNotFoundError("{}".format(filename))

        config = configparser.ConfigParser()
        config.read_file(open(filename))

        log.info("取得配置:file:{},section:{},item:{}".format(filename, section, item))
        return config.get(section, item, fallback='')


    def item_should_exists(self, filename, section, item):
        """
        | 配置项应该存在
        | filename: 配置文件名
        | section: INI配置文件中的Section
        | item: 配置项
        | :return: True OR False
        """
        if not os.path.exists(filename):
            log.error("找不到配置文件: {}".format(filename))
            raise FileNotFoundError("{}".format(filename))

        config = configparser.ConfigParser()
        config.read_file(open(filename))
        return config.has_option(section, item)

    def item_should_not_exists(self, filename, section, item):
        """
        | 判断配置项不应该存在
        | filename: 配置文件名
        | section: INI配置文件中的Section
        | item: 配置项
        | :return: True OR False
        """
        return not self.item_should_exists(filename, section, item)


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

    def has_section(self, conf_file, section):
        config = configparser.ConfigParser()
        config.read_file(open(conf_file))
        return config.has_section(section)

    def get_sections(self, conf_file):
        """
        返回 ``sections`` 列表
        """
        config = configparser.ConfigParser()
        config.read_file(open(conf_file))
        return config.sections()

    def add_section(self, conf_file, section):
        config = configparser.ConfigParser()
        config.read_file(open(conf_file))
        return config.add_section(section)

    def add_item(self, conf_file, section, item, value):
        self.set_item(conf_file, section, item, value, add_new=True)


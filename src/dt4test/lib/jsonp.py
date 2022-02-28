# coding=utf-8

# 通过 jmespath 模块实现结果的 查找与对比
# 外部需求：需要连接数据库取得用户id和key，如果无法连接，可以在 get auth 中根据用户名直接给

import os
import json
import jmespath

from .helper import Helper
from .logger import Logger

log = Logger().get_logger()


class JsonP(Helper):
    """
    处理复杂json的类，主要是用于查询，基于jmespath：https://jmespath.org/tutorial.html
    """
    def expect_json(self, result, item='', exp='', exptype='unicode'):
        """
        | 将测试结果转化成 json 通过 jmespath 进行解析， 与测试用例中的预期进行对比
        | 目前支持的预期结果类型： unicode(默认)、int、float 因为jmespath抽取后就这三种类型
        | result: 待分析的json
        | item: 待抽取的项目
        | exp: 预期值
        | exptype: 类型（默认 unicode）
        | :return: True OR False
        """
        if not (exptype == 'unicode' or exptype == 'int' or exptype == 'float'):
            log.error("Not suppor Compare type:" + exptype + ". Use: int,unicode,float")
            return False

        rjs = json.loads(result)
        r_val = jmespath.search(item, rjs)
        log.info("Expect: " + item + ":" + exp + " >> " + str(r_val))
        if r_val is None:
            log.error("Not Found is result: " + item)
            return False

        exp_val = None

        if exptype == 'unicode':
            exp_val = unicode(exp)
        if exptype == 'int':
            exp_val = int(exp)
        if exptype == 'float':
            exp_val = float(exp)

        if type(r_val) != type(exp_val):
            log.error("Result Type VS Expect Type: " + str(type(r_val)) + " VS " + str(type(exp_val)))
            return False
        if r_val != exp_val:
            log.error("Result Value VS Expect Value: " + str(r_val) + " VS " + str(exp_val))
            return False
        return True


    def get_result(self, result, item, exptype='str'):
        """
        | 返回json内的特定内容，保存结果给下一次请求使用，暂支持str， list返回，后续考虑扩展
        | result: 待分析的json
        | item: jmespath 的表达式
        | exptype: 预期类型（默认 str）
        | :return: result OR ""
        """
        if result.strip().startswith('"') or result.strip().startswith("'"):
            res = result.strip()[1:-1]
        else:
            res = result.strip()
        rjs = json.loads(res)
        r_val = jmespath.search(item, rjs)
        if exptype == 'list':
            return list(r_val)
        return str(r_val)
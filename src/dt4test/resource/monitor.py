import os

import yaml
from yaml.loader import SafeLoader

from ..lib.config_ini import ConfigIni
from ..lib.network import Network
from ..lib.helper import Helper
from ..lib.logger import Logger

from .env import Env

log = Logger().get_logger(__name__)


def show_cli_help():
    """
    显示 客户端帮助
    """
    print(">> monitor list :显示所有monitor")
    print(">> monitor role | role[1]  item :指定节点测试监控项")
    print(">> monitor check plan.yml :测试yml文件中的所有监控是否能正常取得指标")
    print(">> monitor start plan.yml [task_id]:执行监控计划")
    print(">> monitor stop plan_id : 停止监控任务")
    print(">> monitor status :显示所有taskid 和 monitor lists")
    print(">> monitor create monitor_name.sh|.py :创建新的业务监控")


class Monitor(Helper):
    """
    增加监控，删除监控，查看监控信息，启动停止监控

    使用内部配置文件配置通用的监控，使用外部配置文件${PROJECT_DIR}/monitor/monitor_conf.ini配置业务监控

    | 文件格式如下：
    | [cpu_dile]
    | desc = CPU Idle percent
    | script = cpu_idle.sh  ; monitor 目录下面的脚本
    | interval = 15         ; 默认单位都是：秒，这个值可以在执行时的 yml 文件中覆盖
    | unit = percent ; MB | num | qps
    """
    def __init__(self):
        self.confer = ConfigIni()
        self.env = Env()
        self.network = Network()

        self.inner_conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../monitor", "monitor_conf.ini")
        self.outer_conf = os.path.join(self.env.get_project_dir(), "monitor", "monitor_conf.ini")
        self.role_file = self.env.get_roles_file()

        self.webui_ip, self.webui_port = self.env.get_webui_ip_port()
        self.webui_path = self.env.get_webui_api_path()

    def get_monitor_conf_file(self, monitor_item):
        if self.confer.has_section(self.inner_conf, monitor_item):
            return self.inner_conf
        if self.confer.has_section(self.outer_conf, monitor_item):
            return self.outer_conf
        return None

    def get_monitor_type(self, monitor_item):
        if self.confer.has_section(self.inner_conf, monitor_item):
            return "system"
        if self.confer.has_section(self.outer_conf, monitor_item):
            return "service"

        log.error("找不到监控项{} IN {} AND {}".format(monitor_item, self.inner_conf, self.outer_conf))
        raise TypeError("找不到监控项{} IN {} AND {}".format(monitor_item, self.inner_conf, self.outer_conf))

    def get_script(self, monitor_item):
        conf_file = self.get_monitor_conf_file(monitor_item)
        script = self.confer.get_item(conf_file, monitor_item, 'script')
        if script == "":
            log.error("找不到配置项：script IN {} IN {}".format(monitor_item, conf_file))
        return script

    def get_script_file(self, monitor_item):
        conf_file = self.get_monitor_conf_file(monitor_item)
        script = self.confer.get_item(conf_file, monitor_item, 'script')
        return os.path.join(os.path.dirname(conf_file), script)

    def cli(self, argv: []):
        """
        客户端程序接口
        """
        log.info("Argv: {}".format(','.join(argv)))

        # 【check】 用户的监控配置文件在 cli 入口这里check
        if not os.path.exists(self.outer_conf):
            print("Warning:找不到业务的监控配置文件 {}".format(self.outer_conf))
            return 1
        if len(argv) == 2:
            show_cli_help()
            return 0

        if argv[2] == 'list':
            self.list_monitors()
            return 0

        if argv[2] == 'check':
            self.check_yaml(argv[3])
            return 0

        if argv[2] == 'start':
            if len(argv) < 5:
                print("参数错误：应该如：monitor start plan.yaml 20220203_123")
                return 1
            self.start_plan(argv[3], argv[4])

        if argv[2] == 'stop':
            if len(argv) < 4:
                print("参数错误：应该如：monitor stop 20220203_123")
                return 1
            self.stop_plan(argv[3])
            return 0

        if argv[2] == 'create':
            if len(argv) < 4:
                print("参数错误：应该如：monitor create mymonitor.sh|.py")
                return
            self.create_monitor(argv[3])
            return 0

        if len(argv) == 4:
            self.run_monitor_on_role(argv[-2], argv[-1])
            return 0

    def list_monitors(self):
        """
        显示所有配置文件中的monitors
        """

        idx = 0

        def _print(conf_file):
            nonlocal idx
            sections = self.confer.get_sections(conf_file)
            for sc in sections:
                desc = self.confer.get_item(conf_file, sc, 'desc')
                script = self.confer.get_item(conf_file, sc, 'script')
                unit = self.confer.get_item(conf_file, sc, 'unit')
                idx += 1
                print("{}. {}: {} {} unit: {}".format(idx, sc, desc, script, unit))

        print("***** All Monitors ********************************")
        if os.path.exists(self.inner_conf):
            print(">> Monitors in System config :")
            _print(self.inner_conf)
        else:
            msg = "** ERROR: 找不到配置文件：{}".format(self.inner_conf)
            log.error(msg)
            print(msg)

        if os.path.exists(self.outer_conf):
            print(">> Monitors in Service config :")
            _print(self.outer_conf)
        else:
            msg = "** WARN: 找不到配置文件：{}".format(self.outer_conf)
            log.warn(msg)
            print(msg)

    def create_monitor_detail(self, yaml_file, result_file=""):
        """
        通过用户的 ``yaml_file`` 生成监控细节文件 ``result_file`` ，成功返回 ``result_file`` 所有行信息，失败返回[]

        | # Yamle File 样例
        | ---
        |   master:
        |     - cpu_idle:
        |         interval: '21'
        |     - mem_usage
        |
        |   slave:
        |     - cpu_idle
        |     - mem_usage:
        |         interval: 18
        | ...

        | 生成的 ``result_file`` 文件格式（行）：
        | role| ip| port| user| password| home_dir| monitor_item| interval| script| monitor_type

        """

        result_lines = []

        if not os.path.exists(yaml_file):
            log.error("找不到yaml文件：{}".format(yaml_file))
            raise FileNotFoundError("找不到yaml文件：{}".format(yaml_file))

        log.info("解析yaml文件：{}".format(yaml_file))
        data = None
        with open(yaml_file, 'r') as f:
            data = yaml.load(f, Loader=SafeLoader)

        for role in data:      # role: 'master', 'slave'

            role_file = self.role_file

            if not self.confer.has_section(role_file, role):
                log.error("Role:{} In {} ,Not in : {}".format(role, yaml_file, role_file))
                raise TypeError("Role:{} In {} ,Not in : {}".format(role, yaml_file, role_file))

            for item in data[role]:     # item: 'mem_usage' OR {'cpu_idle': {'interval': '21'}}
                interval = 0
                monitor_item = item
                if isinstance(item, dict):
                    for i in item:          # i: 'cpu_idle'
                        monitor_item = i
                        if isinstance(item[i], dict):
                            for j in item[i]:   # j： 'interval'
                                if j == 'interval' or j == 'Interval' :
                                    interval = int(item[i][j])

                monitor_type = self.get_monitor_type(monitor_item)

                conf_file = self.get_monitor_conf_file(monitor_item)
                script = self.confer.get_item(conf_file, monitor_item, 'script')
                if interval == 0:
                    interval = self.confer.get_item(conf_file, monitor_item, 'interval')

                if int(interval) <= 5 or int(interval) >= 120:
                    log.warn("Interval {} 异常，调整为: 15 ".format(interval))
                    interval = '15'

                log.info("解析监控信息 》 模块：{} 监控项：{} interval:{} ".format(role, monitor_item, interval))

                user = self.env.get_user(role)
                password = self.env.get_password(role)
                home_dir = self.env.get_home_dir(role)
                port = self.env.get_ssh_port(role)
                ips = self.env.get_ips(role)
                for ip in ips:
                    log.info("role:{}, ip:{},port:{}, user:{},password:{},home_dir:{},monitor:{},interval:{},script:{},type:{}".format(
                        role, ip, port, user, password, home_dir, monitor_item, interval, script, monitor_type
                    ))
                    line = "{}|{}|{}|{}|{}|{}|{}|{}|{}|{}".format(
                        role, ip, port, user, password, home_dir, monitor_item, interval, script, monitor_type)
                    result_lines.append(line)

        if result_file == "":
            return result_lines

        dir_name = os.path.dirname(result_file)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(result_file, 'w') as f:
            f.write("\n".join(result_lines))
        log.info("监控配置文件生成：{}".format(result_file))

        return result_lines

    def run_monitor_on_role(self, destination, monitor_item):
        """
        在 ``role`` 上调试一个 ``monitor_item``

        role 可以是 role 或者 role[1] 的形式

        返回 监控结果到终端
        """
        index = -1
        if destination.endswith(']'):
            role = destination.split('[')[0]
            index = int(destination.split('[')[1].split(']')[0])
        else:
            role = destination

        user = self.env.get_user(role)
        password = self.env.get_password(role)
        home_dir = self.env.get_home_dir(role)
        port = self.env.get_ssh_port(role)
        ips = self.env.get_ips(role)

        script = self.get_script(monitor_item)
        script_file = self.get_script_file(monitor_item)
        self.env.transfer_script(destination, script_file)

        cmd = home_dir + "/dt_scripts/" + script

        if index >= 0:
            ips = [ips[index]]

        for ip in ips:
            sout, err, status = self.network.ssh_cmd(cmd, ip, user, password, port)
            print("{} {} {}:{}".format(role, ip, monitor_item, sout))
            if err:
                print(err)
                return -1
        return 0

    def run_monitor_once(self, role, ip, port, user, password, home_dir, monitor_item, script):
        """
        指定IP上执行监控指标，用于调试指标
        """
        script_file = self.get_script_file(monitor_item)
        self.env.transfer_script(role, script_file)
        cmd = home_dir + "/dt_scripts/" + script
        sout, err, status = self.network.ssh_cmd(cmd, ip, user, password, port)
        print("{} {} {}:{}".format(role, ip, monitor_item, sout))
        if err:
            print(err)
            return -1
        return 0

    def check_yaml(self, yaml_file):
        """
        调试执行 ``yaml_file`` 中的所有监控项目
        """
        monitors = self.create_monitor_detail(yaml_file)
        for line in monitors:
            (role, ip, port, user, password, home_dir, monitor_item,
             interval, script, monitor_type) = line.strip().split('|')
            self.run_monitor_once(role, ip, port, user, password, home_dir, monitor_item, script)

    def start_plan(self, yaml_file, plan_id):
        """
        执行 ``yaml_file`` 的监控指标信息，以 ``plan_id`` 为一组
        """
        monitors = self.create_monitor_detail(yaml_file)
        for line in monitors:
            (role, ip, port, user, password, home_dir, monitor_item,
             interval, script, monitor_type) = line.strip().split('|')
            script_file = self.get_script_file(monitor_item)
            self.env.transfer_script(role, script_file)

            payload = {"method": "add_monitor", "script_conf": line.strip(), "task_id": str(plan_id)}
            host = self.webui_ip + ":" + self.webui_port
            api_path = self.webui_path

            log.info("添加监控：{} {} {}".format(host,api_path,payload))
            res = self.network.send_post_request(host, api_path, payload)

            assert (res.status_code == 200)
            log.info("添加监控返回：{}".format(res.content))

        print(plan_id)
        return 0

    def stop_plan(self, plan_id):
        """
        调用API接口删除监控指标
        | :param plan_id: plan ID
        | :return:
        """
        payload = {"method": "delete_monitor", "task_id": str(plan_id)}
        host = self.webui_ip + ":" + self.webui_port
        api_path = self.webui_path
        log.info("停止监控计划：{} {} {}".format(host, api_path, payload))
        res = self.network.send_post_request(host, api_path, payload)

        assert (res.status_code == 200)
        log.info("停止监控返回：{}".format(res.content))

        return 0

    def create_monitor(self, monitor_name):
        """
        创建监控模板

        | [cpu_dile]
        | desc = CPU Idle percent
        | script = cpu_idle.sh  ; monitor 目录下面的脚本
        | interval = 15         ; 默认单位都是：秒，这个值可以在执行时的 yml 文件中覆盖
        | unit = % ; MB | num | qps
        """
        if monitor_name.find('.') == -1:
            print("名字错误: Should like cpu_idle.py or cpu_idle.sh")
            return
        script_name = monitor_name
        monitor_item = monitor_name.split('.')[0]

        if self.confer.has_section(self.inner_conf, monitor_item):
            print("名字错误：{} exists in system monitor conf file".format(monitor_item))
            return

        if os.path.exists(self.outer_conf):
            if self.confer.has_section(self.outer_conf, monitor_item):
                print("名字错误：{} exists in service monitor conf file".format(monitor_item))
                return

        service_dir = os.path.dirname(self.outer_conf)
        script_file = os.path.join(service_dir, script_name)

        if os.path.exists(script_file):
            print("无法创建：文件已存在 {}".format(script_file))
            return

        if not os.path.exists(self.outer_conf):
            dir_name = os.path.dirname(self.outer_conf)
            os.makedirs(dir_name) if not os.path.exists(dir_name) else None
            with open(self.outer_conf, 'w') as f:
                f.write("# This is created automatically.")

        self.confer.add_section(self.outer_conf, monitor_item)
        self.confer.add_item(self.outer_conf, monitor_item, 'desc', 'monitor for ' + monitor_item)
        self.confer.add_item(self.outer_conf, monitor_item, 'script', script_name)
        self.confer.add_item(self.outer_conf, monitor_item, 'interval', '15')
        self.confer.add_item(self.outer_conf, monitor_item, 'unit', 'num')

        if script_file.endswith(".sh"):
            with open(script_file, 'w') as f:
                f.write("#!/bin/bash \n")
                f.write("# This is just a monitor example \n")
                f.write("# IMPORTANT: Please just return one VALUE \n")
                f.write('echo "123" \n')
            print("SUCCESS: 你可以编辑 {} ,尝试你的监控了~".format(script_file))
        elif script_file.endswith(".py"):
            with open(script_file, 'w') as f:
                f.write("#!/usr/bin/env python \n")
                f.write("# -*- coding: utf-8 -*- \n")
                f.write("# IMPORTANT: Please just return one VALUE \n")
                f.write('print("123") \n')
            print("SUCCESS: 你可以编辑 {} ,尝试你的监控了~".format(script_file))
        else:
            print("Sorry: 我还没习得此类文件的编写，你可以参考 sh 或 python 的格式")
            return



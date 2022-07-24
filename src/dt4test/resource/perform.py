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
    print(">> perform check plan.yml :尝试通过yaml文件生成用例，检查yaml是否编写错误")
    print(">> perform dryrun plan.yml :模拟执行全部流程，但是不真正的执行具体命令")
    print(">> perform start plan.yml [task_id]:执行测试计划")
    print(">> perform stop plan_id : 停止测试任务")
    print(">> perform status :显示任务运行状态")


class Perform(Helper):
    """
    | 性能稳定性测试库
    | 通过 yaml 文件配置，实现性能稳定性测试的全流程操作
    | 分布式的监控于日志收集
    """
    def __init__(self):
        self.confer = ConfigIni()
        self.env = Env()
        self.network = Network()

        self.timeout = 3600

        self.space2 = ' ' * 2
        self.space4 = ' ' * 4
        self.space8 = ' ' * 8

        self.process_num = 0

        self.case_lines = []

        self.settings = ["***Settings***\n", "Resource    Process\n"]
        self.variables = ["***Variables**\n"]

        self.pre_post = []       # 记录pre 阶段需要后处理的进程
        self.action_post = []    # 记录action 阶段后续需要处理事情
        self.post_post = []

        self.webui_ip, self.webui_port = self.env.get_webui_ip_port()
        self.webui_path = self.env.get_webui_api_path()

    def cli(self, argv: []):
        """
        客户端程序接口
        """
        log.info("Argv: {}".format(','.join(argv)))

        if len(argv) == 2:
            show_cli_help()
            return 0

        if argv[2] == 'check':
            file = self.check_yaml(argv[3])
            print(">> 生成用例文件：{}".format(file))
            return 0

        if argv[2] == 'dryrun':
            self.check_yaml(argv[3])
            return 0

        # if argv[2] == 'start':
        #     if len(argv) < 5:
        #         print("参数错误：应该如：perform start plan.yaml 20220203_123")
        #         return 1
        #     self.start_plan(argv[3], argv[4])
        #
        # if argv[2] == 'stop':
        #     if len(argv) < 4:
        #         print("参数错误：应该如：perform stop 20220203_123")
        #         return 1
        #     self.stop_plan(argv[3])
        #     return 0

        print("无法理解的参数：{}".format(argv))
        return 1

    def get_proc_num(self):
        self.process_num += 1
        return self.process_num

    def add_line(self, aline: str):
        self.case_lines.append(aline + '\n')

    def add_space4_line(self, aline: str):
        self.add_line(self.space4 + aline)

    def add_space8_line(self, aline: str):
        self.add_line(self.space8 + aline)

    def add_post_to_stage(self, stage, c_line):
        if stage == 'pre':
            self.pre_post.append(c_line)
        if stage == 'action':
            self.action_post.append(c_line)
        if stage == 'post':
            self.pre_post.append(c_line)

    def write_one_command(self, stage, cmd_type, cmd, target, timeout, case_file, comment=''):
        self.add_space8_line(comment) if comment else None
        tout = str(timeout) + "s"  # seconds
        alias = "proc_" + str(self.get_proc_num())

        if target == 'local':
            if cmd_type == 'cmdA0':
                t_line = ["${result}=", "Run Process", cmd,
                          "shell=yes",
                          "timeout=" + tout,
                          "stdout_path=${OUTPUTDIR}/" + alias,
                          "stderr_path=${OUTPUTDIR}/" + alias,
                          "on_timeout=kill",
                          "alias=" + alias
                          ]
                c_line = self.space2.join(t_line)
                self.add_space8_line(c_line)

            if cmd_type == 'cmdA1':
                t_line = ["${result}=", "Run Process", cmd,
                          "shell=yes",
                          "timeout=" + tout,
                          "stdout_path=${OUTPUTDIR}/" + alias,
                          "stderr_path=${OUTPUTDIR}/" + alias,
                          "on_timeout=kill",
                          "alias=" + alias
                          ]
                c_line = self.space2.join(t_line)
                self.add_space8_line(c_line)
                t_line = ["Should Be Equal As Integers", "${result.rc}", "0"]
                c_line = self.space2.join(t_line)
                self.add_space8_line(c_line)

            if cmd_type == 'cmdB0':
                t_line = ["Start Process", cmd,
                          "shell=yes",
                          "timeout=" + tout,
                          "stdout_path=${OUTPUTDIR}/" + alias,
                          "stderr_path=${OUTPUTDIR}/" + alias,
                          "on_timeout=kill",
                          "alias=" + alias
                          ]
                c_line = self.space2.join(t_line)
                self.add_space8_line(c_line)

            if cmd_type == 'cmdB1':
                t_line = ["Start Process", cmd,
                          "shell=yes",
                          "timeout=" + tout,
                          "stdout_path=${OUTPUTDIR}/" + alias,
                          "stderr_path=${OUTPUTDIR}/" + alias,
                          "on_timeout=kill",
                          "alias=" + alias
                          ]
                c_line = self.space2.join(t_line)
                self.add_space8_line(c_line)
                t_line = ["${result}=", "Wait For Process", alias]
                c_line = self.space2.join(t_line)
                self.add_post_to_stage(stage, c_line)
                t_line = ["Should Be Equal As Integers", "${result.rc}", "0"]
                c_line = self.space2.join(t_line)
                self.add_post_to_stage(stage, c_line)

            if cmd_type == 'robot':
                t_line = ["${result}=", "Run Process", "robot --outputdir="+"${OUTPUTDIR}/"+alias+" "+case_file,
                          "shell=yes",
                          "timeout=" + tout,
                          "stdout_path=${OUTPUTDIR}/" + alias,
                          "stderr_path=${OUTPUTDIR}/" + alias,
                          "on_timeout=kill",
                          "alias=" + alias
                          ]
                c_line = self.space2.join(t_line)
                self.add_space8_line(c_line)
                t_line = ["Should Be Equal As Integers", "${result.rc}", "0"]
                c_line = self.space2.join(t_line)
                self.add_space8_line(c_line)

            if cmd_type == 'monitor':
                t_line = ["@{ss}=   Split String    ${OUTPUTDIR}   separator=/ ",
                          "${result}=", "Run Process", "dt monitor start " + case_file + " ${ss}[-1]",
                          "shell=yes",
                          "timeout=" + tout,
                          "stdout_path=${OUTPUTDIR}/" + alias,
                          "stderr_path=${OUTPUTDIR}/" + alias,
                          "on_timeout=kill",
                          "alias=" + alias
                          ]
                c_line = self.space2.join(t_line)
                self.add_space8_line(c_line)
                t_line = ["Should Be Equal As Integers", "${result.rc}", "0"]
                c_line = self.space2.join(t_line)
                self.add_space8_line(c_line)

        if target != 'local':
            self.add_line("Not support Non Local.")

    def create_perform_detail(self, yaml_file, result_file=""):
        """
        通过用户的 ``yaml_file`` 生成用例细节文件 ``result_file`` ，成功返回 ``result_file`` 所有行信息，失败返回[]

        | variable：变量配置阶段，目前尚未启用
        | pre： 准备阶段
        | action：测试执行阶段
        | post： 收尾阶段

        | cmdA0: 执行命令，无需检查返回值
        | cmdA1: 执行命令，需要检查返回值，如果返回值非0，则任务失败
        | cmdB0: 后台执行命令，无需检查返回值
        | cmdB1: 后台执行命令，需要检查返回值，如果返回值非0，则任务失败

        | cmdXX：执行命令会处理其输出，及结果，所有 cmd 进程结束时都会被清理
        | cmd: 命令行
        | timeout：超时时间（cmdB不需要）
        | target：执行目标，默认（local本地）

        | robot：这个命令类型会重组robot 用例的输出

        | # Yamle File 样例
        | ---
        |   variable:
        |     - var1:
        |       value: '123'
        |
        |   pre:  # 后续扩展pre自身属性：pass，timeout， etc
        |     - cmdA0:
        |         cmd: 'echo 123'
        |         timeout: 23
        |         target: local
        |     - cmdB0:
        |         cmd: 'mycmd abc.sh'
        |         target: master[1]
        |         pass: true
        |     - monitor:
        |         yaml_file: '../conf/t_monitor.yaml'
        |
        |   action:  # 后续扩展action自身属性： repeat ，step_forward
        |     - cmdA0:
        |         cmd: 'start client'
        |         num: 1
        |     - cmdA1:
        |         cmd: 'start check'
        |   post:
        |     - cmdA1:
        |         cmd: 'create report'
        | ...

        | 生成的 ``result_file`` 文件格式（行）：
        | robot testcase file

        """

        if not os.path.exists(yaml_file):
            log.error("找不到yaml文件：{}".format(yaml_file))
            raise FileNotFoundError("找不到yaml文件：{}".format(yaml_file))

        log.info("解析yaml文件：{}".format(yaml_file))
        data = None
        with open(yaml_file, 'r') as f:
            data = yaml.load(f, Loader=SafeLoader)

        case_name = os.path.splitext(os.path.basename(yaml_file))[0]
        self.add_line(case_name)

        role_list = ['variable', 'pre', 'action', 'post']
        for role in data:      # role: 'pre', 'action', 'post'
            if role not in role_list:
                raise TypeError("Role:{} In {} ,Not in : {}".format(role, yaml_file, role_list))

            if role == 'varialbe':
                # TODO: 处理 变量定义
                continue

            if role == 'pre':
                self.add_space4_line("Log  ** Start pre Stage **")
                self.add_space4_line("TRY")
                for item in data[role]:       # item: 'cmdA0:{} , cmdA1: {cmd: 'xx', target:'', timeout: ' '}'
                    timeout = self.timeout
                    target = 'local'
                    cmd = ''
                    case_file = ''
                    if not isinstance(item, dict):
                        raise TypeError("{}:{} 应该是个字典".format(role,item))
                    for cmd_type in item:    # i: cmdA0
                        perform_item = cmd_type
                        if not isinstance(item[cmd_type], dict):
                            raise TypeError("{}:{}:{} 应该是字典".format(role, item, cmd_type))
                        for attr in item[cmd_type]:  # j： 'cmd' | timeout | target
                            if attr == 'timeout' or attr == 'Timeout':
                                timeout = int(item[cmd_type][attr])
                            if attr == 'target' or attr == 'Target':
                                target = item[cmd_type][attr]
                            if attr == 'cmd' or attr == 'Cmd':
                                cmd = item[cmd_type][attr]
                            if attr == 'case_file' or attr == 'CaseFile' or attr == 'YamlFile' or attr == 'yaml_file':
                                case_file = item[cmd_type][attr]
                        self.write_one_command(role, cmd_type, cmd, target, timeout, case_file)
                role_list.remove(role)
                self.case_lines = self.case_lines + self.pre_post
                self.add_space4_line("EXCEPT")
                self.add_space8_line("Terminate All Processes")
                self.add_space8_line("Fail  ** Pre:异常结束 **")
                self.add_space4_line("ELSE")
                self.add_space8_line("Log  ** Pre:正常结束 **")
                self.add_space4_line("END\n")

            if role == 'action':
                self.add_space4_line("Log  ** Start action Stage **")
                self.add_space4_line("TRY")
                for item in data[role]:       # item: 'cmdA0:{} , cmdA1: {cmd: 'xx', target:'', timeout: ' '}'
                    timeout = self.timeout
                    target = 'local'
                    cmd = ''
                    case_file = ''
                    if not isinstance(item, dict):
                        raise TypeError("{}:{} 应该是个字典".format(role,item))
                    for cmd_type in item:    # i: cmdA0
                        perform_item = cmd_type
                        if not isinstance(item[cmd_type], dict):
                            raise TypeError("{}:{}:{} 应该是字典".format(role, item, cmd_type))
                        for attr in item[cmd_type]:  # j： 'cmd' | timeout | target
                            if attr == 'timeout' or attr == 'Timeout':
                                timeout = int(item[cmd_type][attr])
                            if attr == 'target' or attr == 'Target':
                                target = item[cmd_type][attr]
                            if attr == 'cmd' or attr == 'Cmd':
                                cmd = item[cmd_type][attr]
                            if attr == 'case_file' or attr == 'CaseFile':
                                case_file = item[cmd_type][attr]
                        self.write_one_command(role, cmd_type, cmd, target, timeout, case_file)
                role_list.remove(role)
                self.case_lines = self.case_lines + self.action_post
                self.add_space4_line("EXCEPT")
                self.add_space8_line("Terminate All Processes")
                self.add_space8_line("Fail  ** Action:异常结束 **")
                self.add_space4_line("ELSE")
                self.add_space8_line("Log  ** Action:正常结束 **")
                self.add_space4_line("END\n")

            if role == 'post':
                self.add_space4_line("Log  ** Start post Stage **")
                self.add_space4_line("TRY")
                for item in data[role]:       # item: 'cmdA0:{} , cmdA1: {cmd: 'xx', target:'', timeout: ' '}'
                    timeout = self.timeout
                    target = 'local'
                    cmd = ''
                    case_file = ''
                    if not isinstance(item, dict):
                        raise TypeError("{}:{} 应该是个字典".format(role,item))
                    for cmd_type in item:    # i: cmdA0
                        perform_item = cmd_type
                        if not isinstance(item[cmd_type], dict):
                            raise TypeError("{}:{}:{} 应该是字典".format(role, item, cmd_type))
                        for attr in item[cmd_type]:  # j： 'cmd' | timeout | target
                            if attr == 'timeout' or attr == 'Timeout':
                                timeout = int(item[cmd_type][attr])
                            if attr == 'target' or attr == 'Target':
                                target = item[cmd_type][attr]
                            if attr == 'cmd' or attr == 'Cmd':
                                cmd = item[cmd_type][attr]
                            if attr == 'case_file' or attr == 'CaseFile':
                                case_file = item[cmd_type][attr]
                        self.write_one_command(role, cmd_type, cmd, target, timeout, case_file)
                role_list.remove(role)
                self.case_lines = self.case_lines + self.post_post
                self.add_space4_line("EXCEPT")
                self.add_space8_line("Terminate All Processes")
                self.add_space8_line("Log  ** Post:异常结束 **")
                self.add_space4_line("ELSE")
                self.add_space8_line("Log  ** Post:正常结束 **")
                self.add_space4_line("FINALLY")
                self.add_space8_line("Terminate All Processes")
                self.add_space4_line("END\n")

        file_name = result_file
        if file_name == "":
            file_name = os.path.splitext(yaml_file)[0] + ".robot"

        dir_name = os.path.dirname(file_name)
        if not os.path.exists(dir_name) and not dir_name == '':
            os.makedirs(dir_name)
        with open(file_name, 'w') as f:
            f.write(''.join(self.settings))
            f.write(''.join(self.variables))
            f.write(''.join(self.case_lines))
        log.info("用例文件生成：{}".format(file_name))

        return file_name

    def check_yaml(self, yaml_file):
        """
        调试执行 ``yaml_file`` 中的所有监控项目
        """
        case_file = self.create_perform_detail(yaml_file)
        return case_file


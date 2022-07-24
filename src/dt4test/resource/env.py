import os

from ..lib.config_ini import ConfigIni
from ..lib.network import Network
from ..lib.base import Base
from ..lib.helper import Helper
from ..lib.logger import Logger

log = Logger().get_logger(__name__)


def show_cli_help():
    """
    显示 客户端帮助
    """
    print(">> env master|slave|role :显示所有role的配置ip和user")
    print(">> ssh master|slave|role[1] \"command\" :远程执行命令")
    print(">> sshf master|slave|role[1] command_file :远程执行脚本")
    print(">> scp|put role here.txt there.txt :按role发送文件")
    print(">> get role file_path des_dir : 拉取role上的文件到本地")
    print(">> env create user : 新建roles中的用户")
    print(">> env delete user : 删除roles用户及目录")


class Env(Helper):
    """
    对测试环境进行抽象

    使用 ``PROJECT_DIR/conf`` 目录下的配置文件 ``hosts.txt`` 和 ``roles.ini``

    | ``hosts.txt`` 文件格式：使用root用户进行user创建等操作
    | IP ${SPACES} root_password

    | ``roles.ini`` 文件格式：整个集群的角色的配置, 用户可以扩展
    | [master]
    | ip = 11.12.12.12, 11.12.12.14, 11.12.12.15 ;逗号分割ip
    | user = master
    | password = test@Master
    | home_dir = /data/master
    | ssh_port = 36000
    | process = dollar_master1  ; 通过ps -Aux |grep ``prcess`` 可以检查进程是否存在

    | [slave]
    | (同上，省略)

    Env 提供创建用户的接口，基于上面的配置文件，对于不同的ip进行不同的用户创建

    可以使用系统的 ``config_ini`` 对配置文件进行操作，Env 也提供部分操作方法

    """
    def __init__(self, hostsf=None, rolesf=None):

        self.confer = ConfigIni()    # 用于操作 ini 配置文件
        self.base = Base()
        self.network = Network()

        self.api_path = "/api/v1/task_list/"     # api 调用的 path
        self.project_dir = os.environ.get("PROJECT_DIR", "/tmp")
        self.output_dir = self.project_dir + "/output"
        hosts_file = os.path.join(self.project_dir, "conf", "hosts.txt")
        roles_file = os.path.join(self.project_dir, "conf", "roles.ini")
        log.warn("没有设置环境变量:{}, 使用 /tmp ".format("PROJECT_DIR")) if self.project_dir == "/tmp" else None

        if hostsf:
            self.hosts_file = hostsf
        else:
            self.hosts_file = hosts_file

        if rolesf:
            self.roles_file = rolesf
        else:
            self.roles_file = roles_file

        if not os.path.exists(self.hosts_file):
            log.error("找不到root配置文件：{}".format(self.hosts_file))
        if not os.path.exists(self.roles_file):
            log.error("找不到roles配置文件：{}".format(self.roles_file))

    def cli(self, argv: []):
        """
        客户端接口程序
        """

        # 【check】 roles.ini 的判断在 cli 入口，hosts.txt 的判断在 adduser和deluser 处，避免提前判断造成的干扰
        self._check_roles_file()

        log.info("Argv: {}".format(','.join(argv)))
        if len(argv) == 2:
            show_cli_help()
            return 0

        if len(argv) == 3 and argv[1] == 'env':     # env master|slave|role :显示所有role的配置ip和user
            return self.show_role_info(argv[2])

        if len(argv) == 4 and argv[1:] == ['env', 'create', 'user']:
            return self.create_user()

        if len(argv) == 4 and argv[1:] == ['env', 'delete', 'user']:
            return self.delete_user()

        if len(argv) == 4 and argv[1] == 'ssh':   # ssh master|slave|role[1] \"command\" :远程执行命令
            return self.ssh_cmd(argv[2], argv[3])   #( role , command )

        if len(argv) == 4 and argv[1] == 'sshf':  # sshf master|slave|role[1] command_file :远程执行脚本
            return self.sshf_cmd(argv[2], argv[3])  # ( role , command_file )

        if len(argv) == 5 and argv[1] == 'get':   # get role file_path des_dir: 拉取role上的文件到本地
            return self.get_remote_file(argv[2], argv[3], argv[4])  # ( role , remote_file )

        if len(argv) == 5 and argv[1] in ['scp', 'put']:
            return self.scp_file(argv[2], argv[3], argv[4])  #( role , here ,there )

        print("无法解析的参数：{}".format(argv))
        show_cli_help()
        return -1

    def _check_hosts_file(self):
        if not os.path.exists(self.hosts_file):
            log.error("Error: 找不到配置文件 {}".format(self.hosts_file))
            raise FileNotFoundError("找不到配置文件 {}".format(self.hosts_file))

    def _check_roles_file(self):
        if not os.path.exists(self.roles_file):
            log.error("Error: 找不到配置文件 {}".format(self.roles_file))
            raise FileNotFoundError("找不到配置文件 {}".format(self.roles_file))

    def show_role_info(self, role):
        """
        打印role信息
        :param role: role name
        :return: None
        """
        self._check_roles_file()
        user = self.get_user(role)
        password = self.get_password(role)
        home_dir = self.get_home_dir(role)
        port = self.get_ssh_port(role)
        ips = self.get_ips(role)
        print("{}: ip:{} user:{} password:{} home_dir:{} ssh_port:{}".format(role, ips, user, password, home_dir, port))

    def ssh_cmd(self, destination ,command):
        """
        远程执行命令，支持 role 及 role[1] 的形式

        :return: Success 0 Fail -1
        """
        index = -1
        if destination.endswith(']'):
            role = destination.split('[')[0]
            index = int(destination.split('[')[1].split(']')[0])
        else:
            role = destination

        user = self.get_user(role)
        password = self.get_password(role)
        home_dir = self.get_home_dir(role)
        port = self.get_ssh_port(role)
        ips = self.get_ips(role)

        cmd = command

        if index >= 0:
            sout, err, status = self.network.ssh_cmd(cmd, ips[index], user, password, port)
            print("{} {}:{}".format(role, ips[index], sout))
            if err:
                print(err)
                return -1
            return 0
        else:
            for ip in ips:
                sout, err, status = self.network.ssh_cmd(cmd, ip, user, password, port)
                print("{} {}:{}".format(role, ip, sout))
                if err:
                    print(err)
                    return -1
            return 0

    def sshf_cmd(self, destination, script_file):
        """
        远程执行脚本
        :return:  Success 0 Fail -1
        """
        index = -1
        if destination.endswith(']'):
            role = destination.split('[')[0]
            index = int(destination.split('[')[1].split(']')[0])
        else:
            role = destination

        user = self.get_user(role)
        password = self.get_password(role)
        home_dir = self.get_home_dir(role)
        port = self.get_ssh_port(role)
        ips = self.get_ips(role)

        if not os.path.exists(script_file):
            raise FileNotFoundError("找不到脚本文件 {}".format(script_file))

        self.transfer_script(destination, script_file)

        script = os.path.basename(script_file)
        cmd = home_dir + "/dt_scripts/" + script

        if index >= 0:
            ips = [ips[index]]

        for ip in ips:
            sout, err, status = self.network.ssh_cmd(cmd, ip, user, password, port)
            print("{} {}:{}".format(role, ip, sout))
            if err:
                print(err)
                return -1
        return 0

    def transfer_script(self, destination, script_file):
        """
        传输 script 到目标机器
        """
        index = -1
        if destination.endswith(']'):
            role = destination.split('[')[0]
            index = int(destination.split('[')[1].split(']')[0])
        else:
            role = destination

        user = self.get_user(role)
        password = self.get_password(role)
        home_dir = self.get_home_dir(role)
        port = self.get_ssh_port(role)
        ips = self.get_ips(role)

        src_file = script_file
        file_name = os.path.basename(src_file)
        des_file = os.path.join(home_dir, "dt_scripts", file_name)

        if index >= 0:
            ips = [ips[index]]

        for ip in ips:
            cmd = "mkdir -p {}/dt_scripts".format(home_dir)
            self.network.ssh_cmd(cmd, ip, user, password, port)
            log.info("传输 {} TO {}@{}:{} port:{} ...".format(src_file, user, ip, des_file, port))
            self.network.ssh_upload(src_file, des_file, ip, user, password, port)
            log.info("Finished transfer {}".format(src_file))

        for ip in ips:
            cmd = "chmod +x " + home_dir + "/dt_scripts/*.*"
            self.network.ssh_cmd(cmd, ip, user, password, port)

    def scp_file(self, destination, here, there):
        index = -1
        if destination.endswith(']'):
            role = destination.split('[')[0]
            index = int(destination.split('[')[1].split(']')[0])
        else:
            role = destination

        user = self.get_user(role)
        password = self.get_password(role)
        home_dir = self.get_home_dir(role)
        port = self.get_ssh_port(role)
        ips = self.get_ips(role)

        src_file = here
        file_name = os.path.basename(src_file)
        if not os.path.exists(src_file):
            raise FileNotFoundError("找不到文件 {}".format(src_file))

        if there.endswith('/'):
            if home_dir not in there:
                des_file = os.path.join(home_dir, there, file_name)
            else:
                des_file = os.path.join(there, file_name)
        else:
            if home_dir not in there:
                des_file = os.path.join(home_dir, there)
            else:
                des_file = there

        if index >= 0:
            ips = [ips[index]]

        for ip in ips:
            self.network.ssh_upload(src_file, des_file, ip, user, password, port)

        return 0

    def get_remote_file(self, from_where, remote_file, local_dir):
        index = -1
        if from_where.endswith(']'):
            role = from_where.split('[')[0]
            index = int(from_where.split('[')[1].split(']')[0])
        else:
            role = from_where

        user = self.get_user(role)
        password = self.get_password(role)
        home_dir = self.get_home_dir(role)
        port = self.get_ssh_port(role)
        ips = self.get_ips(role)
        if index >= 0:
            ips = [ips[index]]

        if home_dir not in remote_file:
            src_file = os.path.join(home_dir, remote_file)
        else:
            src_file = remote_file

        file_name = os.path.basename(src_file)

        os.makedirs(local_dir) if not os.path.exists(local_dir) else None
        for ip in ips:
            ip_dir = os.path.join(local_dir, role + '_' + ip)
            os.mkdir(ip_dir)
            des_file = os.path.join(ip_dir, file_name)
            self.network.ssh_download(src_file, des_file, ip, user, password, port)

        return 0

    def create_user(self):
        # TODO: create users in users_file using hosts file
        self._check_hosts_file()
        print("TODO Function")
        pass

    def delete_user(self):
        # TODO: delete users in users_file using hosts file
        self._check_hosts_file()
        print("TODO Function")
        pass

    def auto_ssh(self):
        # TODO: create ssh auto login
        pass

    def get_role(self, section, item):
        """
        取得配置文件中的值
        """
        conf_file = self.roles_file
        return self.confer.get_item(conf_file, section, item)

    def get_ips(self, section):
        """
        返回 ``section`` 的 ip 列表[]
        """
        ip = self.get_role(section, 'ip')
        ips = ip.split(',')
        return [x.strip() for x in ips]

    def get_ip(self, section, idx=1):
        """
        返回单个 ip ，默认第一个
        """
        return self.get_role(section, 'ip')[idx-1]

    def get_user(self, section):
        return self.get_role(section, 'user')

    def get_password(self, section):
        return self.get_role(section, 'password')

    def get_home_dir(self, section):
        return self.get_role(section, 'home_dir')

    def get_ssh_port(self, section):
        return self.get_role(section, 'ssh_port')

    def get_project_dir(self):
        return self.project_dir

    def get_output_dir(self):
        return self.output_dir

    def get_roles_file(self):
        return self.roles_file

    def get_hosts_file(self):
        return self.hosts_file

    def has_role(self, role_name):
        return self.confer.has_section(role_name)

    def get_temp_dir(self):
        rand_name = self.base.gen_outputdir()
        return os.path.join(self.output_dir, rand_name)

    def get_webui_ip_port(self):
        """
        :return: ip,port
        """
        proc_file = self.get_output_dir() + "/.webui.info"

        if not os.path.exists(proc_file):
            log.warn("找不到文件：{}, 请确认webui是否启动".format(proc_file))
            return "127.0.0.1", "8080"

        with open(proc_file, 'r') as f:
            line = f.readline()

        ip, port = line.strip().split()

        return ip, port

    def get_webui_api_path(self):
        return self.api_path



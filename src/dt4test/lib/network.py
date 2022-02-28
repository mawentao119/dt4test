
import requests
import paramiko
import subprocess

from .helper import Helper
from .logger import Logger

log = Logger().get_logger()


class SSHClass:

    def __init__(self, host, user, pwd, port, sshtype=1):
        """
        sshtype 链接类型  1 initexe， 2 initscp， 3 initexe and initscp
        """
        self.host = host
        self.user = user
        self.pwd = pwd
        self.port = port
        self.Error = True
        self.Errorinfo = None
        self.sshtype = sshtype

        self.sshclient = None
        self.scpclient = None
        try:
            self.sshclient, self.scpclient, self.sftp = self.init(self.sshtype)
        except paramiko.AuthenticationException as a:
            self.Error = False
            self.Errorinfo = a
            log.error(self.Errorinfo)
        except Exception as e:
            self.Error = False
            self.Errorinfo = 'Exception: {0}'.format(e)
            log.error(self.Errorinfo)

    def init(self, sshtype):
        # 初始化  链接
        sshclient = None
        scpclient = None
        sftp = None
        if sshtype == 1:
            sshclient = self.initexe()
        elif sshtype == 2:
            scpclient, sftp = self.initscp()
        elif sshtype == 3:
            sshclient = self.initexe()
            scpclient, sftp = self.initscp()
        return sshclient, scpclient, sftp

    def initexe(self):  # 远程 命令 执行 链接初始化
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        log.info("SshClient连接: {} {} {} {} ".format(self.host, self.port, self.user, self.pwd))
        client.connect(self.host, port=self.port, username=self.user, password=self.pwd)
        return client

    def initscp(self):  # scp 文件传输  链接初始化
        # noinspection PyTypeChecker
        log.info("ScpClient连接: {} {} {} {} ".format(self.host, self.port, self.user, self.pwd))
        scpclient = paramiko.Transport((self.host, self.port))
        scpclient.connect(username=self.user, password=self.pwd)
        sftp = paramiko.SFTPClient.from_transport(scpclient)
        return scpclient, sftp

    def getexe(self, command, timeout=120, datatype=1):
        sout = []
        serr = []
        status = 1
        if self.Error and type(command) == str:
            log.info("执行远程命令:{}".format(command))
            stdin, stdout, stderr = self.sshclient.exec_command(command, bufsize=10, timeout=timeout, get_pty=True)
            if datatype == 1:
                # 按照 行 切分的列表
                souttmp = stdout.readlines()
                serrtmp = stderr.readlines()
                for node in souttmp:
                    nodestrip = node.strip('\n').strip('\r')  # 先n再r，顺序不能错
                    sout.append(nodestrip)
                for node in serrtmp:
                    nodestrip = node.strip('\n').strip('\r')  # 先n再r，顺序不能错
                    serr.append(nodestrip)
            else:
                sout = stdout.read()
                serr = stderr.read()

            status = stdout.channel.recv_exit_status()
        else:
            serr = [self.Errorinfo]
        return sout, serr, status

    def getscp(self, sourcepath, distpath, type):
        status = 1
        info = None
        if self.Error:
            try:
                if type == 1:
                    log.info("Put src:{} des:{}".format(sourcepath, distpath))
                    info = self.sftp.put(sourcepath, distpath)
                elif type == 2:
                    log.info("Get src:{} des:{}".format(sourcepath, distpath))
                    info = self.sftp.get(sourcepath, distpath)
                status = 0
            except OSError as e:
                status = 1
                info = str(e)
                log.error(info)
            except Exception as e:
                status = 1
                info = str(e)
                if info == "Failure":
                    info = "Failure, distfile path error"
                log.error(info)
        else:
            info = self.Errorinfo
        return status, info

    def close(self):
        if self.sshclient is not None:
            self.sshclient.close()
        if self.scpclient is not None:
            self.scpclient.close()


class Network(Helper):
    """
    网络服务的公共库
    """
    def send_get_request(self, host, path, payload, headers=None):
        """
        | 发送http get 请求，``payload`` 是json的 key，value 对, http://1.1.1.1:8088/api/someapi
        | :param host: 1.1.1.1:8088
        | :param path: /api/someapi
        | :param payload: {"name":"zhangsan","age":"22"}
        | :param headers: http headers like {"content-type":"json"}
        | :return: request.response
        |
        | **Example** :
        | host = "yourshost.com:8081"
        | payload = {"bid":"110", "model_name":"test_model"}
        | path = "/master/querybid"
        | res = send_get_request(host, path, payload)
        | assert(res.status_code == 200)
        | print(res.content)
        """
        log.info("Send get request:{} {} {} {} ".format(host, path, payload, headers))
        url = 'http://{}{}'.format(host, path)
        response = {}
        try:
            response = requests.get(url, params=payload)
        except Exception as err:
            log.error("send restful request failed, cmd: {0}, payload: {1}, err: {2}".format(url, payload, err))
        return response

    def send_post_request(self, host, path, payload, headers=None):
        """
        | 发送http post 请求，``payload`` 是json的 key，value 对, http://1.1.1.1:8088/api/someapi
        | :param host: 1.1.1.1:8088
        | :param path: /api/someapi
        | :param payload: {"name":"zhangsan","age":"22"}
        | :param headers: http headers like {"content-type":"json"}
        | :return: request.response
        |
        | **Example** :
        | host = "yourshost.com:8081"
        | payload = {"bid":"110", "model_name":"test_model"}
        | path = "/master/querybid"
        | res = send_post_request(host, path, payload)
        | assert(res.status_code == 200)
        | print(res.content)
        """
        log.info("Send post request:{} {} {} {} ".format(host, path, payload, headers))
        url = 'http://{}{}'.format(host, path)
        response = {}
        try:
            response = requests.post(url, data=payload, headers=headers)
        except Exception as err:
            log.error("send restful request failed, cmd: {0}, payload: {1}, err: {2}".format(url, payload, err))
        return response

    def ssh_cmd(self, cmd, host, user, passwd, port, timeout=120, datatype=1):
        """
        | 远程执行 ssh command
        | :param cmd: command
        | :param host:  Host机器
        | :param user: 用户名
        | :param passwd:  密码
        | :param port: ssh port
        | :param timeout: 超时时间
        | :param datatype:  1  initexe
        | :return:
        """
        ssh = None
        try:
            log.info("ssh_cmd参数:{} {} {} {} {} ".format(host, user, passwd, port, cmd))
            ssh = SSHClass(host, user, passwd, int(port), sshtype=1)
            return ssh.getexe(cmd, timeout=timeout, datatype=datatype)
        finally:
            ssh.close()

    def ssh_upload(self, sourcepath, distpath, host, user, passwd, port):
        """
        | Scp 上传文件到远程主机
        | :param sourcepath:
        | :param distpath:
        | :param host:
        | :param user:
        | :param passwd:
        | :param port:
        | :return:
        """
        ssh = None
        try:
            log.info(
                "ssh_upload参数: src:{} des:{} {} {} {} {}".format(sourcepath, distpath, host, user, passwd, port))
            ssh = SSHClass(host, user, passwd, int(port), sshtype=2)
            return ssh.getscp(sourcepath, distpath, 1)
        finally:
            ssh.close()

    def ssh_download(self, sourcepath, distpath, host, user, passwd, port):
        """
        | SCP 从远程主机下载文件
        | :param sourcepath:
        | :param distpath:
        | :param host:
        | :param user:
        | :param passwd:
        | :param port:
        | :return:
        """
        ssh = None
        try:
            log.info(
                "ssh_upload参数: src:{} des:{} {} {} {} {}".format(sourcepath, distpath, host, user, passwd, port))
            ssh = SSHClass(host, user, passwd, int(port), sshtype=2)
            return ssh.getscp(sourcepath, distpath, 2)
        finally:
            ssh.close()

    def curl(self, *varargs):
        """
        | 根据测试用例中的参数 组装 curl 命令,默认加 -s 参数 忽略 -v 参数,如果是 https 默认加 -k 参数
        | :param varargs:
        | :return:
        """
        cmd = 'curl -s '  # 默认使用 -s 参数，为了便于结果处理，可以拷贝 log.html 中的命令，改为 -v参数
        for arg in varargs:
            arg = arg.encode('utf-8')
            log.debug("*ARG:" + arg)
            if arg.startswith('-v'):
                arg = ''
                log.warn(" '-v' cannot use in cases , change to -s ")
            if arg.startswith('-k'):
                arg = ''
                log.debug(" ignor -k, if it is https ,then -k is default .")
            if arg.startswith('https') or arg.startswith("'https"):
                arg = '-k ' + arg
                log.debug(" add -k, it is https.")
            if arg.startswith('-s'):
                arg = ''
            cmd += arg + ' '
        log.info("**CURL: " + cmd)
        p = subprocess.Popen(cmd)
        stdout, stderr = p.communicate()
        return p.returncode, stdout, stderr
import requests
import paramiko
import subprocess

from .helper import Helper
from .logger import Logger

log = Logger().get_logger(__name__)


class SSHClass:

    def __init__(self, host, user, pwd, port, sshtype=1):
        """
        sshtype 链接类型  1 initexe， 2 initscp， 3 initexe and initscp
        """
        self.host = host
        self.user = user
        self.pwd = pwd
        self.port = port
        self.is_error = False
        self.error_info = None
        self.sshtype = sshtype

        self.sshclient = None
        self.scpclient = None
        try:
            self.sshclient, self.scpclient, self.sftp = self.init(self.sshtype)
        except paramiko.AuthenticationException as a:
            self.is_error = True
            self.error_info = a
            log.error(self.error_info)
            raise a
        except Exception as e:
            self.is_error = True
            self.error_info = 'Exception: {0}'.format(e)
            log.error(self.error_info)
            raise e

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

    def getexe(self, command, timeout=120, datatype=1, exec_sudo=False):
        sout = []
        serr = []
        status = 1
        if not self.is_error and type(command) == str:
            log.info("执行远程命令:{}".format(command))
            stdin, stdout, stderr = self.sshclient.exec_command(command, bufsize=10, timeout=timeout, get_pty=True)
            if exec_sudo:
                # 如果要执行sudo，则还需要输入密码
                stdin.write(self.pwd + '\n')
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
            serr = [self.error_info]
        return sout, serr, status

    def getscp(self, sourcepath, distpath, scp_type):
        status = 1
        info = None
        if not self.is_error:
            try:
                if scp_type == 1:
                    log.info("Put src:{} des:{}".format(sourcepath, distpath))
                    info = self.sftp.put(sourcepath, distpath)
                elif scp_type == 2:
                    log.info("Get src:{} des:{}".format(sourcepath, distpath))
                    info = self.sftp.get(sourcepath, distpath)
                status = 0
            except OSError as e:
                status = 1
                info = str(e)
                log.error(info)
                raise e
            except Exception as e:
                status = 1
                info = str(e)
                if info == "Failure":
                    info = "Failure, distfile path error"
                log.error(info)
                raise e
        else:
            info = self.error_info
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

    @staticmethod
    def send_get_request(host, path, payload=None, headers=None, **kwargs):
        """
        | 发送http get 请求，payload是字典格式的键值对, http://1.1.1.1:8088/api/someapi
        | :param host: 1.1.1.1:8088
        | :param path: /api/someapi，host和path拼接出的url为http://1.1.1.1:8088/api/someapi
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
        url = host + path
        log.info("Send get request: {} {} {} ".format(url, payload, headers))

        try:
            response = requests.get(url, params=payload, headers=headers, **kwargs)
            log.info("response status code: %s" % response.status_code)
        except Exception as err:
            log.error("send restful request failed, cmd: {0}, payload: {1}, err: {2}".format(url, payload, err))
            raise err

        return response

    @staticmethod
    def send_post_request(host, path, payload=None, headers=None, **kwargs):
        """
        | 发送http post 请求，payload是json格式的字符串, http://1.1.1.1:8088/api/someapi
        | :param host: 1.1.1.1:8088
        | :param path: /api/someapi，host和path拼接出的url为http://1.1.1.1:8088/api/someapi
        | :param payload: {"name":"zhangsan","age":"22"}
        | :param headers: http headers like {"content-type":"application/json"}
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
        url = host + path
        log.info("Send post request: {} {} {} ".format(url, payload, headers))

        try:
            response = requests.post(url, data=payload, headers=headers, **kwargs)
            log.info("response status code: %s" % response.status_code)
        except Exception as err:
            log.error("send restful request failed, cmd: {0}, payload: {1}, err: {2}".format(url, payload, err))
            raise err

        return response

    @staticmethod
    def send_put_request(host, path, payload=None, headers=None, **kwargs):
        """
        | 发送http put 请求，payload是json格式的字符串, http://1.1.1.1:8088/api/someapi
        | :param host: 1.1.1.1:8088
        | :param path: /api/someapi，host和path拼接出的url为http://1.1.1.1:8088/api/someapi
        | :param payload: {"name":"zhangsan","age":"22"}
        | :param headers: http headers like {"content-type":"application/json"}
        | :return: request.response
        |
        | **Example** :
        | host = "yourshost.com:8081"
        | payload = {"bid":"110", "model_name":"test_model"}
        | path = "/master/querybid"
        | res = send_put_request(host, path, payload)
        | assert(res.status_code == 200)
        | print(res.content)
        """
        url = host + path
        log.info("Send put request: {} {} {} ".format(url, payload, headers))

        try:
            response = requests.put(url, data=payload, headers=headers, **kwargs)
            log.info("response status code: %s" % response.status_code)
        except Exception as err:
            log.error("send restful request failed, cmd: {0}, payload: {1}, err: {2}".format(url, payload, err))
            raise err

        return response

    @staticmethod
    def send_delete_request(host, path, payload=None, headers=None, **kwargs):
        """
        | 发送http delete 请求，payload是json格式的字符串, http://1.1.1.1:8088/api/someapi
        | :param host: 1.1.1.1:8088
        | :param path: /api/someapi，host和path拼接出的url为http://1.1.1.1:8088/api/someapi
        | :param payload: {"name":"zhangsan","age":"22"}
        | :param headers: http headers like {"content-type":"application/x-www-form-urlencoded"}
        | :return: request.response
        |
        | **Example** :
        | host = "yourshost.com:8081"
        | payload = {"bid":"110", "model_name":"test_model"}
        | path = "/master/querybid"
        | res = send_put_request(host, path, payload)
        | assert(res.status_code == 200)
        | print(res.content)
        """
        url = host + path
        log.info("Send delete request: {} {} {} ".format(url, payload, headers))

        try:
            response = requests.delete(url, params=payload, headers=headers, **kwargs)
            log.info("response status code: %s" % response.status_code)
        except Exception as err:
            log.error("send restful request failed, cmd: {0}, payload: {1}, err: {2}".format(url, payload, err))
            raise err

        return response

    @staticmethod
    def ssh_cmd(cmd, host, user, passwd, port, timeout=120, datatype=1):
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
        except Exception as e:
            log.error("远程执行命令失败：{}".format(e))
            raise e
        finally:
            ssh.close()

    @staticmethod
    def ssh_upload(sourcepath, distpath, host, user, passwd, port=36000):
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
        except Exception as e:
            log.error("上传文件失败：{}".format(e))
            raise e
        finally:
            ssh.close()

    @staticmethod
    def ssh_download(sourcepath, distpath, host, user, passwd, port):
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
        except Exception as e:
            log.error("下载文件失败：{}".format(e))
            raise e
        finally:
            ssh.close()

    @staticmethod
    def curl(*varargs):
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
        try:
            log.info("**CURL: " + cmd)
            p = subprocess.Popen(cmd)
            stdout, stderr = p.communicate()
        except Exception as e:
            log.error("Curl命令失败：{}".format(e))
            raise e
        return p.returncode, stdout, stderr


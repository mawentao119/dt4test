# -*- coding: utf-8 -*-

__author__ = "mawentao119@gmail.com"

"""

"""
import os
import paramiko
import codecs
from flask import current_app, session, url_for
import threading
from subprocess import run as subRun, PIPE ,STDOUT
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import json

from robot.api import TestSuiteBuilder, ResultWriter, ExecutionResult    # done
from utils.file import exists_path, make_nod, write_file, read_file, mk_dirs, gen_outputdir
from utils.dbclass import DBcli

from utils.mylogger import getlogger

log = getlogger(__name__)
db_cli = DBcli(os.environ["DB_FILE"])

class SSHClass:

    def __init__(self, host, user, pwd, port, sshtype=1):
        """ sshtype 链接类型  1 initexe， 2 initscp， 3 initexe and initscp"""
        self.log = log

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
            self.log.error(self.Errorinfo)
        except Exception as e:
            self.Error = False
            self.Errorinfo = 'Exception: {0}'.format(e)
            self.log.error(self.Errorinfo)

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
        self.log.info("SshClient连接: {} {} {} {} ".format(self.host, self.port, self.user, self.pwd))
        client.connect(self.host, port=self.port, username=self.user, password=self.pwd)
        return client

    def initscp(self):  # scp 文件传输  链接初始化
        # noinspection PyTypeChecker
        self.log.info("ScpClient连接: {} {} {} {} ".format(self.host, self.port, self.user, self.pwd))
        scpclient = paramiko.Transport((self.host, self.port))
        scpclient.connect(username=self.user, password=self.pwd)
        sftp = paramiko.SFTPClient.from_transport(scpclient)
        return scpclient, sftp

    def getexe(self, command, timeout=120, datatype=1):
        sout = []
        serr = []
        status = 1
        if self.Error and type(command) == str:
            self.log.info("执行远程命令:{}".format(command))
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
                    self.log.info("Put src:{} des:{}".format(sourcepath, distpath))
                    info = self.sftp.put(sourcepath, distpath)
                elif type == 2:
                    self.log.info("Get src:{} des:{}".format(sourcepath, distpath))
                    info = self.sftp.get(sourcepath, distpath)
                status = 0
            except OSError as e:
                status = 1
                info = str(e)
                self.log.error(info)
            except Exception as e:
                status = 1
                info = str(e)
                if info == "Failure":
                    info = "Failure, distfile path error"
                self.log.error(info)
        else:
            info = self.Errorinfo
        return status, info

    def close(self):
        if self.sshclient is not None:
            self.sshclient.close()
        if self.scpclient is not None:
            self.scpclient.close()


def monitor_run(task_no, monitor_item, ip, port, login_user, login_passwd, script):
    ssh = None
    try:
        log.info("Run monitor:{} {} {} {} {} ".format(ip, login_user, login_passwd, port, script))
        ssh = SSHClass(ip, login_user, login_passwd, int(port), sshtype=1)
        (sout, serr, status) = ssh.getexe(script, timeout=30, datatype=0)
        log.info("Monitor Res:{},{},{}".format(status, sout, serr))
        if status == 0:
            val = str(sout, encoding="utf-8").strip()
            info = ""
        else:
            val = "0"
            info = str(serr, encoding="utf-8").strip()
    finally:
        ssh.close()

    time_now = time.strftime("%Y%m%d%H%M%S", time.localtime())
    db_cli.insert_monitor(task_no, ip, monitor_item, time_now, val, info)

def get_monitor_info(task_id="TODO"):
    # monitors = [
    #     {'no': '1', 'name': '1.2.3.4|cpu_idle|%', 'time': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04'],
    #      'data': [2, 5, 1, 6]},
    #     {'no': '2', 'name': '1.2.3.4|mem_fre|sum', 'time': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04'],
    #      'data': [1, 8, 4, 6]},
    #     {'no': '3', 'name': '1.2.3.4|io_bus|time', 'time': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04'],
    #      'data': [7, 3, 2, 4]}
    # ]
    once_limit = 10
    monitors = []
    # select distinct(name) from (select ip || '|' || monitor_item as name from monitor where task_no='1234');
    sql = '''select distinct(name) from (select ip || '|' || monitor_item as name from monitor);'''
    res = db_cli.runsql(sql)

    monitor_num = 0
    for i in res:
        (name,) = i
        monitor_num += 1
        mnt = {'no': monitor_num, 'name': name, 'time': [], 'data': []}
        monitors.append(mnt)

    for m in monitors:
        (ip, monitor_item) = m['name'].split('|')
        sql = '''select time_now,value from monitor where ip='{}' and monitor_item='{}' 
                                 order by time_now desc limit {} ;'''.format(ip, monitor_item, once_limit)

        res_new = db_cli.runsql(sql)
        for item in res_new:
            (time_now, value) = item
            m['time'].append(time_now)
            m['data'].append(value)

    return monitors

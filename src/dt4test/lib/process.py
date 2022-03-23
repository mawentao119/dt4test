from robot.libraries.Process import Process
from robot.libraries.OperatingSystem import OperatingSystem

from .helper import Helper
from .logger import Logger

log = Logger().get_logger(__name__)


class Proc(Helper):
    """
    | 本地进程操作
    | 借用`s`RF``的 `Process <https://github.com/robotframework/robotframework/blob/master/src/robot/libraries/Process.py>`_
    | 借用``RF``的 `OperatingSystem <https://github.com/robotframework/robotframework/blob/master/src/robot/libraries/OperatingSystem.py>`_
    | 参考：charisma/ideate/blob/master/common/resource/process.resource
    | 核心参数说明：
    | **configuration**：
    | def __init__(self, cwd=None, shell=False, stdout=None, stderr=None, stdin='PIPE',output_encoding='CONSOLE', alias=None, env=None, \*\*rest):
    |     self.cwd = self._get_cwd(cwd)
    |     self.shell = is_truthy(shell)
    |     self.alias = alias
    |     self.output_encoding = output_encoding
    |     self.stdout_stream = self._new_stream(stdout)
    |     self.stderr_stream = self._get_stderr(stderr, stdout, self.stdout_stream)
    |     self.stdin_stream = self._get_stdin(stdin)
    |     self.env = self._construct_env(env, rest)

    | **ExecuteResult**：
    | def __init__(self, process, stdout, stderr, stdin=None, rc=None,output_encoding=None):
    |     self._process = process
    |     self.stdout_path = self._get_path(stdout)
    |     self.stderr_path = self._get_path(stderr)
    |     self.rc = rc
    |     self._output_encoding = output_encoding
    |     self._stdout = None
    |     self._stderr = None
    |     self._custom_streams = [stream for stream in (stdout, stderr, stdin) if self._is_custom_stream(stream)]

    | **command and arguments**：
    |     conf = ProcessConfiguration(\*\*configuration)
    |     command = conf.get_command(command, list(arguments))
    |     self._log_start(command, conf)
    |     process = subprocess.Popen(command, \*\*conf.popen_config)
    |     self._results[process] = ExecutionResult(process, \*\*conf.result_config)
    |     self._processes.register(process, alias=conf.alias)
    |     return self._processes.current
    |
    """
    def __init__(self):
        self.proc = Process()
        self.os = OperatingSystem()

    def run(self, command):
        """
        | 执行command命令，返回（返回值，标准输出）
        | :param command: command
        | :return: (rc, output)
        """
        log.info("执行命令:{}".format(command))
        return self.os.run(command)

    def run_process(self, command, *arguments, **configuration):
        """
        执行一个进程，并等待其结束
        
        | **Examples** :
        | res = run_process("python", "-c", "print('Hello world')")
        | assert res.stdout == "Hello world"
        | assert res.rc == 0
        """
        return self.proc.run_process(command, *arguments, **configuration)

    def start_process(self, command, *arguments, **configuration):
        """
        后台执行进程，立即返回 
        
        | **Examples** :
        | p1 = start_process("sleep 10", shell=True, alias="mysleep1")
        | p2 = start_process("sleep 2", shell=True, alias="mysleep2")
        | process_should_be_running("mysleep1")
        | terminate_process("mysleep1")
        | process_should_be_stopped("mysleep1")
        | wait_for_process(handle="mysleep2", timeout="3s", on_timeout="kill")  # Caution: Do not use time.sleep
        | res1 = get_process_result("mysleep1")
        | res2 = get_process_result("mysleep2")
        | assert res1.rc == -15
        | assert res2.rc == 0
        """
        return self.proc.start_process(command, *arguments, **configuration)

    def get_process_id(self, handle=None):
        """
        取得进程ID，默认当前活跃进程id
        """
        return self.proc.get_process_id(handle)

    def get_process_object(self, handle=None):
        """
        取得进程示例，Process 示例
        """
        return self.proc.get_process_object(handle)

    def get_process_result(self, handle=None, rc=False, stdout=False,
                           stderr=False, stdout_path=False, stderr_path=False):
        """
        取得进程结果
        """
        return self.proc.get_process_result(handle, rc, stdout, stderr, stdout_path, stderr_path)

    def is_process_running(self, handle=None):
        """
        进程是否在执行
        """
        return self.proc.is_process_running(handle)

    def join_command_line(self, *args):
        """
        连接命令行
        """
        return self.proc.join_command_line(*args)

    def send_signal_to_process(self, signal, handle=None, group=False):
        """
        向进程发送信号量
        """
        return self.proc.send_signal_to_process(signal, handle, group)

    def split_command_line(self, args, escaping=False):
        """
        拆分命令行
        """
        return self.proc.split_command_line(args, escaping)

    def switch_process(self, handle):
        """
        切换当前活跃进程
        """
        return self.proc.switch_process(handle)

    def terminate_process(self, handle=None, kill=False):
        """
        Stops the process gracefully or forcefully.
        """
        return self.proc.terminate_process(handle, kill)

    def terminate_all_processes(self, kill=False):
        """
        停止所有启动的进程
        """
        return self.proc.terminate_all_processes(kill)

    def wait_for_process(self, handle=None, timeout=None, on_timeout='continue'):
        """
        等待进程结束
        """
        return self.proc.wait_for_process(handle, timeout, on_timeout)


PROC = Proc()

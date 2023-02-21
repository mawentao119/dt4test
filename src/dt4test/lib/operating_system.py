import os.path
import zipfile

from robot.libraries.OperatingSystem import OperatingSystem

from .helper import Helper
from .logger import Logger

log = Logger().get_logger(__name__)


class OPSystem(Helper):
    """
    | 本地进程操作
    """
    def __init__(self):
        self.os = OperatingSystem()

    def set_environment_variable(self, name, value):
        """
        设置环境变量
        """
        return self.os.set_environment_variable(name, value)

    def append_to_environment_variable(self, name, *values, **config):
        """
        追加环境变量

        If the environment variable already exists, values are added after it,
        and otherwise a new environment variable is created.

        """
        return self.os.append_to_environment_variable(name, *values, **config)

    def remove_environment_variable(self, *names):
        """
        删除环境变量
        """
        return self.os.remove_environment_variable(*names)

    def create_file(self, path, content='', encoding='UTF-8'):
        """
        创建文件，内容为content
        """
        return self.os.create_file(path, content, encoding)

    def append_to_file(self, path, content, encoding='UTF-8'):
        """
        追加内容到文件
        """
        return self.os.append_to_file(path, content, encoding)

    def get_file(self, path, encoding='UTF-8', encoding_errors='strict'):
        """
        取得文件内容
        """
        return self.os.get_file(path, encoding, encoding_errors)

    def create_directory(self, path):
        """
        创建目录
        """
        return self.os.create_directory(path)

    def remove_directory(self, path, recursive=False):
        """
        删除目录
        """
        return self.os.remove_directory(path, recursive)

    def copy_directory(self, source, destination):
        """
        拷贝目录
        """
        return self.os.copy_directory(source, destination)

    def copy_file(self, source, destination):
        """
        拷贝文件
        """
        return self.os.copy_file(source, destination)

    def remove_files(self, *paths):
        """
        删除多个文件
        """
        return self.os.remove_files(*paths)

    def empty_directory(self, path):
        """
        清空目录
        """
        return self.os.empty_directory(path)

    def count_items_in_directory(self, path, pattern=None):
        """
        统计文件和目录数:
        """
        return self.os.count_items_in_directory(path, pattern)

    def count_files_in_directory(self, path, pattern=None):
        """
        统计文件数
        """
        return self.os.count_files_in_directory(path, pattern)

    def count_directories_in_directory(self, path, pattern=None):
        """
        统计目录数
        """
        return self.os.count_directories_in_directory(path, pattern)

    def get_modified_time(self, path, format='timestamp'):
        """
        取得修改时间

        How time is returned is determined based on the given ``format``
        string as follows. Note that all checks are case-insensitive.
        Returned time is also automatically logged.

        1) If ``format`` contains the word ``epoch``, the time is returned
           in seconds after the UNIX epoch. The return value is always
           an integer.

        2) If ``format`` contains any of the words ``year``, ``month``,
           ``day``, ``hour``, ``min`` or ``sec``, only the selected parts are
           returned. The order of the returned parts is always the one
           in the previous sentence and the order of the words in
           ``format`` is not significant. The parts are returned as
           zero-padded strings (e.g. May -> ``05``).

        3) Otherwise, and by default, the time is returned as a
           timestamp string in the format ``2006-02-24 15:08:31``.

        """
        return self.os.get_modified_time(path, format)

    def set_modified_time(self, path, mtime):
        """
        设置修改时间

        Changes the modification and access times of the given file to
        the value determined by ``mtime``. The time can be given in
        different formats described below. Note that all checks
        involving strings are case-insensitive. Modified time can only
        be set to regular files.

        1) If ``mtime`` is a number, or a string that can be converted
           to a number, it is interpreted as seconds since the UNIX
           epoch (1970-01-01 00:00:00 UTC). This documentation was
           originally written about 1177654467 seconds after the epoch.

        2) If ``mtime`` is a timestamp, that time will be used. Valid
           timestamp formats are ``YYYY-MM-DD hh:mm:ss`` and
           ``YYYYMMDD hhmmss``.

        3) If ``mtime`` is equal to ``NOW``, the current local time is used.

        4) If ``mtime`` is equal to ``UTC``, the current time in
           [http://en.wikipedia.org/wiki/Coordinated_Universal_Time|UTC]
           is used.

        5) If ``mtime`` is in the format like ``NOW - 1 day`` or ``UTC + 1
           hour 30 min``, the current local/UTC time plus/minus the time
           specified with the time string is used. The time string format
           is described in an appendix of Robot Framework User Guide.

        """
        return self.os.set_modified_time(path, mtime)

    def zip_file(self, output_file, *input_files):
        """
        将多个文件压缩成zip文件
        :param output_file: zip 文件名
        :param input_files: 输入文件列表
        :return:
        """

        with open(output_file, 'w') as zf:
            for f in input_files:
                if not os.path.isfile(f):
                    log.error("Do not support DIR now. 不支持目录:{}".format(f))
                    raise RuntimeError("现在还不支持目录:{}".format(f))
                zf.write(f)



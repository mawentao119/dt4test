from robot.libraries.String import String
from robot.libraries.Collections import Collections
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.OperatingSystem import OperatingSystem

from .helper import Helper
from .logger import Logger

log = Logger().get_logger(__name__)


class Expectation(Helper):
    """
    | Assertions
    """
    def __init__(self):
        self.string = String()
        self.collect = Collections()
        self.builtin = BuiltIn()
        self.os = OperatingSystem()

    def length_should_be(self, item, length, msg=None):
        """
        长度应该是
        """
        return self.builtin.length_should_be(item, length, msg)

    def should_be_empty(self, item, msg=None):
        """
        应该为空
        """
        return self.builtin.should_be_empty(item, msg)

    def should_not_be_empty(self, item, msg=None):
        """
        应该非空
        """
        return self.builtin.should_not_be_empty(item, msg)

    def should_exist(self, path, msg=None):
        """
        文件或目录应该存在
        """
        return self.os.should_exist(path, msg)

    def should_not_exist(self, path, msg=None):
        """
        文件或目录应该不存在
        """
        return self.os.should_not_exist(path, msg)

    def should_be_equal_as_integers(self, first, second, msg=None, values=True, base=None):
        """
        作为整数相等

        | **Examples** :
        | should_be_equal_as_integers('42',42,'Error message')
        | should_be_equal_as_integers('ABCD','abcd',base=16)
        | should_be_equal_as_integers('0b1011','11')
        """
        return self.builtin.should_be_equal_as_integers(first, second, msg, values, base)

    def should_not_be_equal_as_integers(self, first, second, msg=None, values=True, base=None):
        """
        作为整数应该不相等
        """
        return self.builtin.should_not_be_equal_as_integers(first, second, msg, values, base)

    def should_not_be_equal_as_numbers(self, first, second, msg=None, values=True, precision=6):
        """
        作为数值应该不相等
        """
        return self.builtin.should_not_be_equal_as_numbers(first, second, msg, values, precision)

    def should_be_equal_as_numbers(self, first, second, msg=None, values=True, precision=6):
        """
        作为数值应该相等
        """
        return self.builtin.should_be_equal_as_numbers(first, second, msg, values, precision)

    def should_not_be_equal_as_strings(self, first, second, msg=None, values=True,
                                       ignore_case=False, strip_spaces=False,
                                       collapse_spaces=False):
        """
        作为字符串不相等
        """
        return self.builtin.should_not_be_equal_as_strings(first, second, msg, values, ignore_case,
                                                           strip_spaces, collapse_spaces)

    def should_be_equal_as_strings(self, first, second, msg=None, values=True,
                                   ignore_case=False, strip_spaces=False,
                                   formatter='str', collapse_spaces=False):
        """
        作为字符串相等
        """
        return self.builtin.should_be_equal_as_strings(first, second, msg, values, ignore_case,
                                                           strip_spaces, formatter, collapse_spaces)

    def should_contain(self, container, item, msg=None, values=True,
                       ignore_case=False, strip_spaces=False, collapse_spaces=False):
        """
        Fails if ``container`` does not contain ``item`` one or more times.
        """
        return self.builtin.should_contain(container, item, msg, values, ignore_case, strip_spaces, collapse_spaces)

    def should_not_contain(self, container, item, msg=None, values=True,
                           ignore_case=False, strip_spaces=False, collapse_spaces=False):
        """
        The ``container`` does not contain ``item``
        """
        return self.builtin.should_not_contain(container, item, msg, values, ignore_case, strip_spaces, collapse_spaces)

    def should_contain_any(self, container, *items, **configuration):
        """
        应该包含任意一个，Python ``in`` 操作

        Supports additional configuration parameters ``msg``, ``values``,
        ``ignore_case`` and ``strip_spaces``, and ``collapse_spaces``
        which have exactly the same semantics as arguments with same
        names have with `Should Contain`. These arguments must always
        be given using ``name=value`` syntax after all ``items``.

        | **Examples** :
        | should_contain_any( alist, item1, item2, item3)
        | should_contain_any( alist, item1, item2, item3, ignore_case=True)

        """
        return self.builtin.should_contain_any(container, *items, **configuration)

    def should_not_contain_any(self, container, *items, **configuration):
        """
        应该不包含任意一个，Python ``not in`` 操作
        """
        return self.builtin.should_not_contain_any(container, *items, **configuration)

    def should_contain_x_times(self, container, item, count, msg=None,
                               ignore_case=False, strip_spaces=False, collapse_spaces=False):
        """
        应该包含 X 次
        """
        return self.builtin.should_contain_x_times(container, item, count, msg, ignore_case,
                                                   strip_spaces, collapse_spaces)

    def should_match(self, string, pattern, msg=None, values=True, ignore_case=False):
        """
        Fails if the given ``string`` does not match the given ``pattern``.

        Pattern matching is similar as matching files in a shell with
        ``*``, ``?`` and ``[chars]`` acting as wildcards.

        """
        return self.builtin.should_match(string, pattern, msg, values, ignore_case)

    def should_match_regexp(self, string, pattern, msg=None, values=True):
        """
        Fails if ``string`` does not match ``pattern`` as a regular expression.

        Notice that the given pattern does not need to match the whole string.
        For example, the pattern ``ello`` matches the string ``Hello world!``.
        If a full match is needed, the ``^`` and ``$`` characters can be used
        to denote the beginning and end of the string, respectively.
        For example, ``^ello$`` only matches the exact string ``ello``.

        """
        return self.builtin.should_match_regexp(string, pattern, msg, values)

    def should_not_match(self, string, pattern, msg=None, values=True, ignore_case=False):
        """
        应该不匹配模式
        """
        return self.builtin.should_not_match(string, pattern, msg, values, ignore_case)

    def should_not_match_regexp(self, string, pattern, msg=None, values=True):
        """
        应该不匹配正则
        """
        return self.builtin.should_not_match_regexp(string, pattern, msg, values)

    def dictionaries_should_be_equal(self, dict1, dict2, msg=None, values=True):
        """
        字典应该相等
        """
        return self.collect.dictionaries_should_be_equal(dict1, dict2, msg, values)

    def dictionary_should_contain_value(self, dictionary, value, msg=None):
        """
        字典应该包含值
        """
        return self.collect.dictionary_should_contain_value(dictionary, value, msg)

    def dictionary_should_not_contain_value(self, dictionary, value, msg=None):
        """
        字典不应该包含值
        """
        return self.collect.dictionary_should_not_contain_value(dictionary, value, msg)

    def dictionary_should_contain_item(self, dictionary, key, value, msg=None):
        """
        字典应该包含元素
        """
        return self.collect.dictionary_should_contain_item(dictionary, key, value, msg)

    def dictionary_should_contain_key(self, dictionary, key, msg=None):
        """
        字典应该包含 key
        """
        return self.collect.dictionary_should_contain_key(dictionary, key, msg)

    def dictionary_should_not_contain_key(self, dictionary, key, msg=None):
        """
        字典不应该包含key
        """
        return self.collect.dictionary_should_not_contain_key(dictionary, key, msg)

    def list_should_contain_sub_list(self, list1, list2, msg=None, values=True):
        """
        列表应该包含子列表
        """
        return self.collect.list_should_contain_sub_list(list1, list2, msg, values)

    def list_should_contain_value(self, list_, value, msg=None):
        """
        列表应该包含值
        """
        return self.collect.list_should_contain_value(list_, value, msg)

    def list_should_not_contain_value(self, list_, value, msg=None):
        """
        列表应该不包含值
        """
        return self.collect.list_should_not_contain_value(list_, value, msg)

    def list_should_not_contain_duplicates(self, list_, msg=None):
        """
        列表应该不包含重复的值
        """
        return self.collect.list_should_not_contain_duplicates(list_, msg)

    def lists_should_be_equal(self, list1, list2, msg=None, values=True, names=None, ignore_order=False):
        """
        列表应该相等
        """
        return self.collect.lists_should_be_equal(list1, list2, msg, values, names, ignore_order)

    def should_contain_match(self, list, pattern, msg=None, case_insensitive=False, whitespace_insensitive=False):
        """
        列表应该包含模式
        """
        return self.collect.should_contain_match(list, pattern, msg, case_insensitive, whitespace_insensitive)

    def should_not_contain_match(self, list, pattern, msg=None, case_insensitive=False, whitespace_insensitive=False):
        """
        列表不应该包含模式
        """
        return self.collect.should_not_contain_match(list, pattern, msg, case_insensitive, whitespace_insensitive)

    def should_be_byte_string(self, item, msg=None):
        """
        应该是字节串
        """
        return self.string.should_be_byte_string(item, msg)

    def should_be_lower_case(self, string, msg=None):
        """
        应该全是小写
        """
        return self.string.should_be_lower_case(string, msg)

    def should_be_upper_case(self, string, msg=None):
        """
        应该全是大写
        """
        return self.string.should_be_upper_case(string, msg)

    def should_be_unicode_string(self, item, msg=None):
        """
        应该是unicode串
        """
        return self.string.should_be_unicode_string(item, msg)

    def directory_should_be_empty(self, path, msg=None):
        """
        目录应该为空
        """
        return self.os.directory_should_be_empty(path, msg)

    def directory_should_not_be_empty(self, path, msg=None):
        """
        目录应该非空
        """
        return self.os.directory_should_not_be_empty(path, msg)

    def directory_should_exist(self, path, msg=None):
        """
        目录应该存在
        """
        return self.os.directory_should_exist(path, msg)

    def directory_should_not_exist(self, path, msg=None):
        """
        目录应该不存在
        """
        return self.os.directory_should_not_exist(path, msg)

    def file_should_be_empty(self, path, msg=None):
        """
        文件应该为空
        """
        return self.os.file_should_be_empty(path, msg)

    def file_should_not_be_empty(self, path, msg=None):
        """
        文件应该非空
        """
        return self.os.file_should_not_be_empty(path, msg)

    def file_should_exist(self, path, msg=None):
        """
        文件应该存在
        """
        return self.os.file_should_exist(path, msg)

    def file_should_not_exist(self, path, msg=None):
        """
        文件应该不存在
        """
        return self.os.file_should_not_exist(path, msg)



from robot.libraries.String import String
from robot.libraries.Collections import Collections
from robot.libraries.BuiltIn import BuiltIn

from .helper import Helper
from .logger import Logger

log = Logger().get_logger(__name__)


class Element(Helper):
    """
    | 测试用到的简单数据
    | 借用`s`RF``的 `Sting <https://github.com/robotframework/robotframework/blob/master/src/robot/libraries/Sting.py>`_
    | 借用``RF``的 `Collections <https://github.com/robotframework/robotframework/blob/master/src/robot/libraries/Collections.py>`_
    | 借用``RF``的 `BuiltIn <https://github.com/robotframework/robotframework/blob/master/src/robot/libraries/BuiltIn.py>`_
    """
    def __init__(self):
        self.string = String()
        self.collect = Collections()
        self.builtin = BuiltIn()

    def convert_to_binary(self, item, base=None, prefix=None, length=None):
        """
        | 转成二进制
        | **Examples** :
        | convert_to_binary('10') # Result is 1010
        | convert_to_binary('F', base=16, prefix=0b) # Result is 0b1111
        | convert_to_binary('-2',prefix=B ,length=4) # Result is -B0010
        """
        return self.builtin.convert_to_binary(item, base, prefix, length)

    def convert_to_octal(self, item, base=None, prefix=None, length=None):
        """
        | 转成10进制
        | **Examples** :
        | convert_to_octal('10') # Result is 12
        | convert_to_octal('-F', base=16, prefix=0) # Result is -017
        | convert_to_octal('16', prefix=oct, length=4) # Result is oct0020
        """
        return self.builtin.convert_to_octal(item, base, prefix, length)

    def convert_to_hex(self, item, base=None, prefix=None, length=None, lowercase=False):
        """
        | 转成16进制
        | **Examples** :
        | convert_to_hex(255) # Result is FF
        | convert_to_hex(-10,length=2)# Result is -0x0A
        | convert_to_hex('255', prefix='X') # Result is Xff
        """
        return self.builtin.convert_to_hex(item, base, prefix, length, lowercase)

    def convert_to_boolean(self, item):
        """
        | 转成布尔型
        """
        return self.builtin.convert_to_boolean(item)

    def convert_to_bytes(self, input, input_type='text'):
        """
        | 转换成字节(样例结果参见源码)
        | **Examples** : (最后一列是返回值，显示异常参考源码):
        | convert_to_bytes('hyvä)  # hyv\xe4
        | convert_to_bytes('hyv\xe4') # hyv\xe4
        | convert_to_bytes('\xff\x07') # \xff\x07
        | convert_to_bytes(' 82 70','int') # RF
        | convert_to_bytes('0b10 0x10','int')  # \x02\x10
        | convert_to_bytes('ff 00 07','hex') # \xff\x00\x07
        | convert_to_bytes('52462121','hex')  # RF!!
        | convert_to_bytes('0000 1000','bin') # \x08
        | convert_to_bytes([1,2,12],'int') # \x01\x02\x0c
        | convert_to_bytes([1,2,12],'hex') #  \x01\x02\x12

        """
        return self.builtin.convert_to_bytes(input, input_type)

    def convert_to_integer(self, item, base=None):
        """
        | 转成整形数
        | **Examples** :
        | convert_to_integer(100)  # Result is 100
        | convert_to_integer('FF AA', 16)   # Result is 65450
        | convert_to_integer('100',8) # Result is 64
        | convert_to_integer('-100',2) # Result is -4
        | convert_to_integer('0b100') # Result is 4
        | convert_to_integer('-0x100') # Result is -256
        """
        return self.builtin.convert_to_integer(item, base)

    def convert_to_number(self, item, precision=None):
        """
        | 字符串转成数字
        | **Examples** :
        | convert_to_number(42.512) # Result is 42.512
        | convert_to_number('42.512','1') # Result is 42.5
        | convert_to_number(42.512,0) # Result is 43.0
        | convert_to_number(42.512,-1 ) # Result is 40.0
        """
        return self.builtin.convert_to_number(item, precision)

    def convert_to_string(self, item):
        """
        | 转成字符串
        .. warning::
            Use `Encode String To Bytes` and `Decode Bytes To String` keywords
            in ``String`` library if you need to convert between Unicode and byte
            strings using different encodings. Use `Convert To Bytes` if you just
            want to create byte strings.

        """
        return self.builtin.convert_to_string(item)

    def decode_bytes_to_string(self, bytes, encoding, errors='strict'):
        """
        解码 ``bytes`` 到 Unicode string 使用 ``encoding``.

        ``errors`` argument controls what to do if decoding some bytes fails.
        All values accepted by ``decode`` method in Python are valid, but in
        practice the following values are most useful:

        - ``strict``: fail if characters cannot be decoded (default)
        - ``ignore``: ignore characters that cannot be decoded
        - ``replace``: replace characters that cannot be decoded with a replacement character

        | **Examples**:
        | decode_bytes_to_string( bytes,'UTF-8')
        | decode_bytes_to_string(bytes,'ASCII',errors='ignore')

        Use `Encode String To Bytes` if you need to convert Unicode strings to
        byte strings, and `Convert To String` in ``BuiltIn`` if you need to
        convert arbitrary objects to Unicode strings.

        """
        return self.string.decode_bytes_to_string(bytes, encoding, errors)

    def encode_string_to_bytes(self, string, encoding, errors='strict'):
        """
        编码字符串 string 到 字节 使用 encodeing

        ``errors`` argument controls what to do if encoding some characters fails.
        All values accepted by ``encode`` method in Python are valid, but in
        practice the following values are most useful:

        - ``strict``: fail if characters cannot be encoded (default)
        - ``ignore``: ignore characters that cannot be encoded
        - ``replace``: replace characters that cannot be encoded with a replacement character

        | **Examples** :
        | encode_string_to_bytes(string,'UTF-8')
        | encode_string_to_bytes(string,'ASCII',errors='ignore')

        Use `Convert To Bytes` in ``BuiltIn`` if you want to create bytes based
        on character or integer sequences. Use `Decode Bytes To String` if you
        need to convert byte strings to Unicode strings and `Convert To String`
        in ``BuiltIn`` if you need to convert arbitrary objects to Unicode.
        """
        return self.string.encode_string_to_bytes(string, encoding, errors)

    def generate_random_string(self, length=8, chars='[LETTERS][NUMBERS]', prefix=''):
        """
        生成指定长度的随机串，使用特定chars

        ``length`` can be given as a number, a string representation of a number,
        or as a range of numbers, such as ``5-10``. When a range of values is given
        the range will be selected by random within the range.

        The population sequence ``chars`` contains the characters to use
        when generating the random string. It can contain any
        characters, and it is possible to use special markers
        explained in the table below:

        | |  = Marker =   |               = Explanation =                   |
        | ``[LOWER]``   | Lowercase ASCII characters from ``a`` to ``z``. |
        | ``[UPPER]``   | Uppercase ASCII characters from ``A`` to ``Z``. |
        | ``[LETTERS]`` | Lowercase and uppercase ASCII characters.       |
        | ``[NUMBERS]`` | Numbers from 0 to 9.                            |
        | ``prefix``    | String's prefix |

        | **Examples** :
        | generate_random_string()
        | generate_random_string(12, '[LOWER]')
        | generate_random_string(8,'01')
        | generate_random_string(4,'[NUMBERS]abcdef')
        | generate_random_string('5-10')

        Giving ``length`` as a range of values is new in Robot Framework 5.0.
        """
        new_length = length - len(prefix)
        if new_length > 0:
            return prefix + self.string.generate_random_string(new_length, chars)
        else:
            log.warn("{}- prefix {} < 0, omit prefix".format(prefix))
            return self.string.generate_random_string(length, chars)

    def get_lines_containing_string(self, string, pattern, case_insensitive=False):
        """
        从 ``string`` 中取得包含 `pattern`` 的行

        The ``pattern`` is always considered to be a normal string, not a glob
        or regexp pattern. A line matches if the ``pattern`` is found anywhere
        on it.

        The match is case-sensitive by default, but giving ``case_insensitive``
        a true value makes it case-insensitive. The value is considered true
        if it is a non-empty string that is not equal to ``false``, ``none`` or
        ``no``. If the value is not a string, its truth value is got directly
        in Python.

        Lines are returned as one string catenated back together with
        newlines. Possible trailing newline is never returned. The
        number of matching lines is automatically logged.

        | **Examples** :
        | get_lines_containing_string(somestring,'FAIL', case_insensitive=False)

        See `Get Lines Matching Pattern` and `Get Lines Matching Regexp`
        if you need more complex pattern matching.
        """
        return self.string.get_lines_containing_string(string, pattern, case_insensitive)

    def get_lines_matching_pattern(self, string, pattern, case_insensitive=False):
        """
        从 ``string`` 中取得匹配 ``pattern`` 的行.

        | The ``pattern`` is where:
        | ``*``        | matches everything |
        | ``?``        | matches any single character |
        | ``[chars]``  | matches any character inside square brackets (e.g. ``[abc]`` matches either ``a``, ``b`` or ``c``) |
        | ``[!chars]`` | matches any character not inside square brackets |

        A line matches only if it matches the ``pattern`` fully.

        The match is case-sensitive by default, but giving ``case_insensitive``
        a true value makes it case-insensitive. The value is considered true
        if it is a non-empty string that is not equal to ``false``, ``none`` or
        ``no``. If the value is not a string, its truth value is got directly
        in Python.

        Lines are returned as one string catenated back together with
        newlines. Possible trailing newline is never returned. The
        number of matching lines is automatically logged.

        | **Examples** :
        | get_lines_matching_pattern(result, 'Wild???? example')
        | get_lines_matching_pattern(result, 'FAIL: *')
        """
        return self.string.get_lines_matching_pattern(string, pattern, case_insensitive)

    def get_lines_matching_regexp(self, string, pattern, partial_match=False):
        """
        从 ``string`` 中取得匹配正则 ``pattern`` 的行.

        By default lines match only if they match the pattern fully, but
        partial matching can be enabled by giving the ``partial_match``
        argument a true value. The value is considered true
        if it is a non-empty string that is not equal to ``false``, ``none`` or
        ``no``. If the value is not a string, its truth value is got directly
        in Python.

        If the pattern is empty, it matches only empty lines by default.
        When partial matching is enabled, empty pattern matches all lines.

        Notice that to make the match case-insensitive, you need to prefix
        the pattern with case-insensitive flag ``(?i)``.

        Lines are returned as one string concatenated back together with
        newlines. Possible trailing newline is never returned. The
        number of matching lines is automatically logged.

        | **Examples** :
        | get_lines_matching_regexp(result，'Reg\\\\w{3} example')
        | get_lines_matching_regexp(result，'Reg\\\\w{3} example',partial_match=True)
        | get_lines_matching_regexp(result，'(?i)FAIL: .*')
        """
        return self.string.get_lines_matching_regexp(string, pattern, partial_match)

    def get_regexp_matches(self, string, pattern, *groups):
        """
        返回匹配的列表

        Returns a list of all non-overlapping matches in the given string.

        ``string`` is the string to find matches from and ``pattern`` is the
        regular expression. See `BuiltIn.Should Match Regexp` for more
        information about Python regular expression syntax in general and how
        to use it in Robot Framework data in particular.

        If no groups are used, the returned list contains full matches. If one
        group is used, the list contains only contents of that group. If
        multiple groups are used, the list contains tuples that contain
        individual group contents. All groups can be given as indexes (starting
        from 1) and named groups also as names.

        | **Examples** :
        | get_regexp_matches('the string','xxx')
        | get_regexp_matches('the string','t..')
        | get_regexp_matches('the string','t(..)', 1)
        | get_regexp_matches('the string','t(?P<name>..)', 'name')
        | get_regexp_matches('the string', 't(.)(.)',1,2)
        | =>
        | ${no match} = []
        | ${matches} = ['the', 'tri']
        | ${one group} = ['he', 'ri']
        | ${named group} = ['he', 'ri']
        | ${two groups} = [('h', 'e'), ('r', 'i')]
        """
        return self.string.get_regexp_matches(string, pattern, *groups)

    def remove_string(self, string, *removables):
        """
        删除串中的内容

        Removes all ``removables`` from the given ``string``.

        ``removables`` are used as literal strings. Each removable will be
        matched to a temporary string from which preceding removables have
        been already removed. See second example below.

        Use `Remove String Using Regexp` if more powerful pattern matching is
        needed. If only a certain number of matches should be removed,
        `Replace String` or `Replace String Using Regexp` can be used.

        A modified version of the string is returned and the original
        string is not altered.

        | **Examples** :
        | remove_string('Robot Framework','work')'  # Robot Frame
        | remove_string('Robot Framework','o','bt') # R Framewrk
        """
        return self.string.remove_string(string, *removables)

    def remove_string_using_regexp(self, string, *patterns):
        """
        使用模式匹配删除 ``string`` 中的内容

        This keyword is otherwise identical to `Remove String`, but
        the ``patterns`` to search for are considered to be a regular
        expression. See `Replace String Using Regexp` for more information
        about the regular expression syntax. That keyword can also be
        used if there is a need to remove only a certain number of
        occurrences.

        """
        return self.string.remove_string_using_regexp(string, *patterns)

    def replace_string(self, string, search_for, replace_with, count=-1):
        """
        替换串

        Replaces ``search_for`` in the given ``string`` with ``replace_with`` for ``count`` times.

        ``search_for`` is used as a literal string. See `Replace String
        Using Regexp` if more powerful pattern matching is needed.
        If you need to just remove a string see `Remove String`.

        If the optional argument ``count`` is given, only that many
        occurrences from left are replaced. Negative ``count`` means
        that all occurrences are replaced (default behaviour) and zero
        means that nothing is done.

        | **Examples** :
        | replace_string('Hello, world!','world','tellus') # Hello, tellus!
        | replace_string('Hello, world!','l','',count=1) #  Helo, world!

        """
        return self.string.replace_string(string,search_for, replace_with, count)

    def replace_string_using_regexp(self, string, pattern, replace_with, count=-1):
        """
        正则替换串

        | **Examples** :
        | replace_string_using_regexp(string, '20\\\\d\\\\d-\\\\d\\\\d-\\\\d\\\\d',<DATE>)
        | replace_string_using_regexp(string, '(Hello|Hi)','', count=1)
        """
        return self.string.remove_string_using_regexp(string, pattern, replace_with, count)

    def get_index_from_list(self, list_, value, start=0, end=None):
        """
        得到列表中的索引

        Returns the index of the first occurrence of the ``value`` on the list.

        The search can be narrowed to the selected sublist by the ``start`` and
        ``end`` indexes having the same semantics as with `Get Slice From List`
        keyword. In case the value is not found, -1 is returned. The given list
        is never altered by this keyword.

        """
        return self.collect.get_index_from_list(list_, value, start, end)

    def copy_list(self, list_, deepcopy=False):
        """
        拷贝列表，``deepcopy`` for deepcopy
        """
        return self.collect.copy_list(list_, deepcopy)

    def copy_dictionary(self, dictionary, deepcopy=False):
        """
        拷贝字典，``deepcopy`` for deepcopy
        """
        return self.collect.copy_dictionary(dictionary, deepcopy)

    def insert_into_list(self, list_, index, value):
        """
        在 ``index`` 处插入列表元素
        """
        return self.collect.insert_into_list(list_, index, value)

    def set_list_value(self, list_, index, value):
        """
        设置list ``index`` 的值
        """
        return self.collect.set_list_value(list_, index, value)

    def remove_from_list(self, list_, index):
        """
        按 ``index`` 删除列表元素
        """
        return self.collect.remove_from_list(list_, index)

    def remove_values_from_list(self, list_, *values):
        """
        删除列表元素 ``values``
        """
        return self.collect.remove_values_from_list(list_, *values)

    def reverse_list(self, list_):
        """
        列表倒序
        """
        return self.collect.reverse_list(list_)

    def pop_from_dictionary(self, dictionary, key, default=None):
        """
        从字典中弹出 ``key`` , 返回 value
        """
        return self.collect.pop_from_dictionary(dictionary, key, default)

    def remove_duplicates(self, list_):
        """
        列表去重
        """
        return self.collect.remove_duplicates(list_)

    def remove_from_dictionary(self, dictionary, *keys):
        """
        从字典中删除 ``keys``
        """
        return self.collect.remove_from_dictionary(dictionary, *keys)

    def set_to_dictionary(self, dictionary, *key_value_pairs, **items):
        """
        设置字典的值

        | **Example** ：
        | set_to_dictionary( dict, 'key1','value1','key2','value2', key3='value3', key4='value4')
        """
        return self.collect.set_to_dictionary(dictionary, *key_value_pairs, **items)




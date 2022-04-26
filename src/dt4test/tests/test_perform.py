import os

from ..resource.perform import Perform

class TestPerform:
    def test_yaml_to_case(self):
        pf = Perform()
        content = '''
# Yamle File 样例
---
  variable:
    - var1:
      value: '123'

  pre:  # 后续扩展pre自身属性：pass，timeout， etc
    - cmdA0:
        cmd: 'echo 123'
        timeout: 23
        target: local
    - cmdB0:
        cmd: 'mycmd abc.sh'
        target: master[1]
        pass: true
    - monitor:
        yaml_file: '../conf/t_monitor.yaml'

  action:  # 后续扩展action自身属性： repeat ，step_forward
    - cmdA0:
        cmd: 'start client'
        num: 1
    - cmdA1:
        cmd: 'start check'
  post:
    - cmdA1:
        cmd: 'create report'
        '''

        with open("test_xxx.yaml", 'w') as f:
            f.write(content)

        pf.check_yaml("test_xxx.yaml")

        os.remove("test_xxx.yaml")
        os.remove("test_xxx.robot")


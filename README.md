# Dt4test
A library for distributed big data system test

### Installation
```
pip install dt4test
```

### Get started
* use ``dt`` comman 
```commandline
***********dt4test client***************
Log file:/data1/dollarkv4/test_dir/output/dt4test.log
Module Logger:可以通过传入log文件名，指定log文件，如果没有 ${PROJECT_DIR}环境变量，则放在 /tmp 目录下面
Module Network:网络服务的公共库
Module Base:基础的公共函数
Module JsonP:处理复杂json的类，主要是用于查询，基于jmespath：https://jmespath.org/tutorial.html
Module ConfigIni:INI 格式的配置文件的处理，get ，set ，if exists
Module CaseRunner:Run Test Case
```
* import modules
```Python
from dt4test import network

host = "yourshost.com:8081"
payload = {"bid":"110", "model_name":"test_model"}
path = "/master/querybid"
res = network.send_get_request(host, path, payload)
assert(res.status_code == 200)
print(res.content)

```
#### Get All Apis
```Python
from dt4test import network
network.help()
```

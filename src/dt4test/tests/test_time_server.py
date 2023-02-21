# -*- coding: utf-8 -*-

######################################################
# Test Scheduler and RuleCheck
######################################################

__author__ = "mawentao119@gmail.com"

import time

from ..resource.time_server import TimeServerData
from ..resource.time_server_checkrule import CheckRule
from ..resource.time_server_serviceproxy import ServiceProxy


class TestSchedulerTester:

    def test_tsd_get_start_time(self):
        sc = TimeServerData()
        res = sc.get_start_time()
        assert res["status"] == "success"

    def test_tsd_remove_task(self):
        sc = TimeServerData()
        res = sc.remove_task(task_id="t1")
        assert res["status"] == "success"

    def test_tsd_remove_inst(self):
        sc = TimeServerData()
        res = sc.remove_inst("iid1")
        assert res["status"] == "success"

    def test_tsd_get_insts_bytes(self):
        sc = TimeServerData()
        res = sc.get_insts_bytes()
        assert res["status"] == "success"

    def test_get_tasks_bytes(self):
        sc = TimeServerData()
        res = sc.get_tasks_bytes()
        assert res["status"] == "success"

    def test_get_insts_bytes(self):
        sc = TimeServerData()
        res = sc.get_insts_bytes()
        assert res["status"] == "success"

    def test_get_task_record(self):
        sc = TimeServerData()
        res = sc.get_task_record(task_id="t1")
        assert res["status"] == "success"

    ##################################  SERVICE ####################################################

    def test_update_date(self):
        sc = ServiceProxy()
        res = sc.update_data()
        assert res["status"] == "success"

    def test_add_one_task(self):
        sc = ServiceProxy()
        res = sc.add_one_task("t1")
        assert res["status"] == "success"

    def test_add_one_inst(self):
        sc = ServiceProxy()
        res = sc.add_one_inst("iid1")
        assert res["status"] == "success"

    def test_init_service(self):
        sc = ServiceProxy()
        path = "/Users/mawentao/PycharmProjects/data-test/dt4test/src/dt4test/webui/utils/time_server/service"
        file = "proxy_service.py"
        res = sc.init_service(path, file)
        assert res["status"] == "success"

    def test_clear_data(self):
        sc = ServiceProxy()
        res = sc.clear_data()
        assert res["status"] == "success"

    def test_clear_tasks(self):
        sc = ServiceProxy()
        res = sc.clear_tasks()
        assert res["status"] == "success"

    def test_clear_insts(self):
        sc = ServiceProxy()
        res = sc.clear_insts()
        assert res["status"] == "success"

    def test_del_task(self):
        sc = ServiceProxy()
        res = sc.del_task("t1")
        assert res["status"] == "success"

    def test_del_inst(self):
        sc = ServiceProxy()
        res = sc.del_inst("iid1")
        assert res["status"] == "success"

    ##################################  RULE ####################################################

    def test_update_rule(self):
        sc = CheckRule()
        res = sc.update_rule("/Users/mawentao/PycharmProjects/data-test/dt4test/src/dt4test/webui/utils/time_server/rules")
        assert res["status"] == "success"

    def test_add_one_rule(self):
        sc = CheckRule()
        file = "example_rule.py"
        rule_dir = "/Users/charisma/PythonProjects/dt4test/src/dt4test/webui/utils/time_server/rules"
        res = sc.add_one_rule(file, rule_dir)
        assert res["status"] == "success"

    def test_remove_one_rule(self):
        sc = CheckRule()
        name = "example_rule.Rule"
        res = sc.remove_one_rule(name)
        assert res["status"] == "success"

    def test_run_one_rule(self):
        sc = CheckRule()
        name = "example_rule.Rule"
        res = sc.run_one_rule(name)
        assert res["status"] == "success"

    def test_run_all_rule(self):
        sc = CheckRule()
        res = sc.run_all_rule()
        assert res["status"] == "success"

    def test_get_all_rule(self):
        sc = CheckRule()
        res = sc.get_all_rule()
        assert res["status"] == "success"

    def test_get_report(self):
        sc = CheckRule()
        res = sc.get_report()
        assert res["status"] == "success"

    def test_get_rule_report(self):
        sc = CheckRule()
        name = "example_rule.Rule"
        res = sc.get_rule_report(name)
        assert res["status"] == "success"

    ######################################### System test case #######################

    def test_system(self):
        tsd = TimeServerData()
        cr = CheckRule()
        sv = ServiceProxy()

        # check TimerServerData
        res = tsd.get_start_time()
        assert res["status"] == "success"

        # init rule
        res = cr.update_rule(
            "/Users/mawentao/PycharmProjects/data-test/dt4test/src/dt4test/webui/utils/time_server/rules")
        assert res["status"] == "success"

        # init service
        path = "/Users/mawentao/PycharmProjects/data-test/dt4test/src/dt4test/webui/utils/time_server/service"
        file = "proxy_service.py"
        res = sv.init_service(path, file)
        assert res["status"] == "success"

        # put into data
        for i in range(1,5):
            res = sv.update_data()
            assert res["status"] == "success"
            time.sleep(1)

        # run rule
        res = cr.run_all_rule()
        assert res["status"] == "success"

    ##################### Test update and rulecheck loop ##########################

    def test_start_update_data(self):
        tsd = TimeServerData()
        cr = CheckRule()
        sv = ServiceProxy()

        res = sv.set_update_interval(15)
        assert res["status"] == "success"
        res = sv.start_update()
        assert res["status"] == "success"

        res = cr.set_check_interval(20)
        assert res["status"] == "success"
        res = cr.start_do_check()
        assert res["status"] == "success"

        time.sleep(60)

        res = cr.stop_do_check()
        assert res["status"] == "success"

        res = sv.stop_update()
        assert res["status"] == "success"


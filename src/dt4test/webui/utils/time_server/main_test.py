# -*- utf-8 -*-

###############################################################
# Test Scheduler system
# __author__ = "mawentao119@gmail.com"
# __datetime__ = "2023-02-11 17:43:00"
###############################################################
import os
import time

from scheduler_data import Scheduler
from checkrules import CheckRules
from serviceinterface import ServiceProxy
from common import get_time_now
from threading import Thread

from mylogger import getlogger

log = getlogger(__name__)


def service_update_loop(interval: int, service):
    while True:
        time.sleep(interval)
        log.info("Start Running Data Update:{} ...".format(get_time_now()))
        service.update_tasks()
        service.update_insts()
        log.info("Finished Update date:{}".format(get_time_now()))


def service_update_runner(interval: int, service):
    run_all_runner = Thread(target=service_update_loop, args=(interval, service))
    run_all_runner.start()
    return run_all_runner


def checkrule_loop(interval: int, checkrule):
    while True:
        time.sleep(interval)
        log.info("Start CheckRule Update:{} ...".format(get_time_now()))
        checkrule.do_check()
        log.info("Finished CheckRule Update:{}".format(get_time_now()))

def checkrule_runner(interval: int, checkrule):
    cr_runner = Thread(target=checkrule_loop, args=(interval, checkrule))
    cr_runner.start()
    return cr_runner


def report_loop(interval: int, checkrule):
    while True:
        time.sleep(interval)
        checkrule.get_report()


def report_runner(interval: int, checkrule):
    rpt_run = Thread(target=report_loop, args=(interval, checkrule))
    rpt_run.start()
    return rpt_run

def main():
    sc = Scheduler()
    cr = CheckRules(sc)
    sv = ServiceProxy(sc)

    service_path = os.path.join(os.getcwd(), "service")
    sv.init_service(service_path, "proxy_service.py")

    rule_path = os.path.join(os.getcwd(), "rules")
    cr.update_rules(rule_path)

    # 下面三组任务，分线程执行，本别进行 周期性数据更新，规则执行，报告输出
    # sv.update_tasks()
    # sv.update_insts()
    log.info("启动周期更新数据线程...")
    update_runner = service_update_runner(5, sv)

    # cr.do_check()
    log.info("启动周期执行Rule线程...")
    check_runner = checkrule_runner(10, cr)

    log.info("启动报告输出线程...")
    # print(cr.get_report())
    ret_runner = report_runner(15, cr)

    log.info("系统启动完成")


if __name__ == "__main__":
    main()

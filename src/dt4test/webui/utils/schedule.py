# -*- coding: utf-8 -*-

__author__ = "mawentao119@gmail.com"

"""

"""

import os
import threading
from datetime import datetime
from utils.run import robot_run
from utils.monitor_run import monitor_run
from utils.mylogger import getlogger

log = getlogger(__name__)


def add_schedulejob(app, scheduler, args):
    user = args['user']
    schedule_type = args["schedule_type"]

    if schedule_type not in ["interval","cron","date"] :
        return {"status": "fail", "msg": "暂不支持这种调度:{}".format(schedule_type)}

    (project, task_name, task_no) = (args['project'], args['task_name'], args['task_no'])

    cmdfile = app.config["OUTPUT_DIR"] + "/{}/cmd.txt".format(task_no)
    if not os.path.isfile(cmdfile):
        return {"status": "fail", "msg": "无法找到命令文件:{}".format(cmdfile)}

    cmdline = ''
    with open(cmdfile, 'r') as f:
        cmdline = f.readline()

    cmdline = cmdline.strip()
    if cmdline == '':
        return {"status": "fail", "msg": "命令文件为空."}

    log.info("rerun_task CMD:" + cmdline)

    splits = cmdline.split('|')

    cases = splits[-1]  # driver|robot|args|output=xxx|cases
    jobargs = splits[2]

    job_id = "{}#{}#{}".format(task_no, user, project)

    lock = threading.Lock()
    lock.acquire()
    job = scheduler.get_job(job_id)
    if job:
        lock.release()
        return {"status": "fail", "msg": "Error: 该调度任务已存在！"}
    else:
        year = int(args["year"]) if args["year"] !='' else 0
        mon = int(args["mon"]) if args["mon"] !='' else 0
        day = int(args["day"]) if args["day"] !='' else 0
        hour = int(args["hour"]) if args["hour"] !='' else 0
        min = int(args["min"]) if args["min"] !='' else 0
        sec = int(args["sec"]) if args["sec"] !='' else 0

        if schedule_type == 'date':
            log.info("Add date schedulejob:(year,mon,day,hour,min,sec):{},{},{},{},{},{}".format(year,mon,day,hour,min,sec))
            try:
                scheduler.add_job(id=job_id,
                                  name=user,
                                  func=robot_run,
                                  args=(cases, jobargs, user, schedule_type),
                                  trigger=schedule_type,
                                  run_date=datetime(year,mon,day,hour,min,sec)
                                  )
            except Exception as e:
                lock.release()
                return {"status": "fail", "msg": "Error: 调度任务添加失败:{}".format(e)}

        elif schedule_type == 'interval':
            weeks = int(args["week"]) if args["week"] else 0
            start_date = args["start_date"]
            end_date = args["end_date"]

            log.info("Add interval schedulejob:weeks,days,hours,minutes,seconds,start_date,end_date:{},{},{},{},{},{},{}".format(weeks,day,hour,min,sec,start_date,end_date))

            try:
                if start_date and end_date:
                    scheduler.add_job(id=job_id,
                                      name=user,
                                      func=robot_run,
                                      args=(cases, jobargs, user, schedule_type),
                                      trigger=schedule_type,
                                      weeks = weeks,
                                      days = day,
                                      hours = hour,
                                      minutes = min,
                                      seconds = sec,
                                      start_date = start_date,
                                      end_date = end_date
                                      )
                else:
                    scheduler.add_job(id=job_id,
                                      name=user,
                                      func=robot_run,
                                      args=(cases, jobargs, user, schedule_type),
                                      trigger=schedule_type,
                                      weeks=weeks,
                                      days=day,
                                      hours=hour,
                                      minutes=min,
                                      seconds=sec
                                      )
            except Exception as e:
                lock.release()
                return {"status": "fail", "msg": "Error: 调度任务添加失败:{}".format(e)}

        else:   #cron
            year = int(args["year"]) if args["year"] != '' else "*"
            mon = int(args["mon"]) if args["mon"] != '' else "*"
            day = int(args["day"]) if args["day"] != '' else "*"
            hour = int(args["hour"]) if args["hour"] != '' else "*"
            min = int(args["min"]) if args["min"] != '' else "*"
            sec = int(args["sec"]) if args["sec"] != '' else "*"
            week = int(args["week"]) if args["week"] != '' else "*"
            day_of_week = int(args["day_of_week"]) if args["day_of_week"] != '' else "*"

            start_date = args["start_date"]
            end_date = args["end_date"]

            log.info("Add cron schedulejob:year:{},month:{},day:{},week:{},dayofweek:{},hour:{},minute:{},second:{},start_date:{},end_date:{}".format(year,mon,day,week,day_of_week,hour,min,sec,start_date,end_date))

            try:
                if start_date and end_date:
                    scheduler.add_job(id=job_id,
                                      name=user,
                                      func=robot_run,
                                      args=(cases, jobargs, user, schedule_type),
                                      trigger=schedule_type,
                                      year = year,
                                      month = mon,
                                      day = day,
                                      week=week,
                                      day_of_week = day_of_week,
                                      hour = hour,
                                      minute = min,
                                      second = sec,
                                      start_date = start_date,
                                      end_date = end_date
                                      )
                else:
                    scheduler.add_job(id=job_id,
                                      name=user,
                                      func=robot_run,
                                      args=(cases, jobargs, user, schedule_type),
                                      trigger=schedule_type,
                                      year=year,
                                      month=mon,
                                      day=day,
                                      week=week,
                                      day_of_week=day_of_week,
                                      hour=hour,
                                      minute=min,
                                      second=sec
                                      )
            except Exception as e:
                lock.release()
                return {"status": "fail", "msg": "Error: 调度任务添加失败:{}".format(e)}

    lock.release()
    return {"status": "success", "msg": "新增调度任务成功:{}".format(job_id)}


def add_monitorjob(scheduler, args):
    task_no = args["task_no"]
    ip = args['user']
    monitor_item = args["project"]
    script = args["task_name"]
    login_user = args["login_user"]
    login_passwd = args["login_passwd"]
    login_port = args["login_port"]

    schedule_type= args["schedule_type"]

    job_id = "{}#{}#{}".format(task_no, ip, monitor_item)

    lock = threading.Lock()
    lock.acquire()
    job = scheduler.get_job(job_id)
    if job:
        lock.release()
        return {"status": "success", "msg": "monitor already exists."}
    else:
        sec = int(args["sec"]) if args["sec"] !='' else 15    # 默认 15 秒
        log.info("Add monitor job args:{} ".format( args ))
        try:
            scheduler.add_job(id=job_id,
                              name=ip,
                              func=monitor_run,
                              args=(task_no, monitor_item, ip, login_port, login_user, login_passwd, script),
                              trigger=schedule_type,
                              weeks=0,
                              days=0,
                              hours=0,
                              minutes=0,
                              seconds=sec
                              )
        except Exception as e:
            lock.release()
            return {"status": "fail", "msg": "Error: 调度任务添加失败:{}".format(e)}

    lock.release()
    return {"status": "success", "msg": "新增调度任务成功:{}".format(job_id)}

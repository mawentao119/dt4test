# -*- coding: utf-8 -*-

__author__ = "苦叶子"
__modifier__ = "mawentao119@gmail.com"

"""

"""

from flask import current_app, session, url_for
from flask_restful import Resource, reqparse
import json
import os
import codecs
import threading
from dateutil import tz

from robot.api import ExecutionResult   # done

from utils.file import exists_path
from utils.run import remove_robot
from ..app import scheduler
from utils.schedule import add_schedulejob, add_monitorjob
from utils.mylogger import getlogger


class TaskList(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('method', type=str)
        self.parser.add_argument('task_no', type=str)
        self.parser.add_argument('user', type=str)
        self.parser.add_argument('project', type=str)
        self.parser.add_argument('task_name', type=str)
        self.parser.add_argument('schedule_type', type=str)
        self.parser.add_argument('year', type=str)
        self.parser.add_argument('mon', type=str)
        self.parser.add_argument('day', type=str)
        self.parser.add_argument('hour', type=str)
        self.parser.add_argument('min', type=str)
        self.parser.add_argument('sec', type=str)
        self.parser.add_argument('week', type=str)
        self.parser.add_argument('day_of_week', type=str)
        self.parser.add_argument('start_date', type=str)
        self.parser.add_argument('end_date', type=str)
        self.parser.add_argument('script_conf', type=str)
        self.parser.add_argument('task_id', type=str)
        self.log = getlogger(__name__)
        self.app = current_app._get_current_object()

    def get(self):
        args = self.parser.parse_args()
        if args['method'] == 'get_tasklist':
            project = args["project"]
            return get_task_list(self.app, self.app.config['USER_NAME'], project)
        if args['method'] == 'get_schedulejoblist':
            return get_schedulejob_list(self.app, args)

    def post(self):
        args = self.parser.parse_args()

        if args["method"] == "pause":        # pause one job
            (task_no, user, project, task_name) = (args['task_no'], args['user'], args['project'], args['task_name'])
            job_id = "{}#{}#{}".format(task_no, user, project)

            lock = threading.Lock()
            lock.acquire()

            try:
                scheduler.pause_job(job_id)
            except Exception as e:
                lock.release()
                return {"status": "fail", "msg": "失败:{}".format(e)}

            lock.release()

            self.app.config['DB'].insert_loginfo(os.environ["USER_NAME"], 'schedulejob', 'pause', job_id, 'success')
            return {"status": "success", "msg": "成功：冻结任务:{}".format(job_id)}

        elif args["method"] == "resume":
            (task_no, user,project,task_name) = (args['task_no'], args['user'],args['project'],args['task_name'])
            job_id = "{}#{}#{}".format(task_no, user, project)

            lock = threading.Lock()
            lock.acquire()

            try:
                scheduler.resume_job(job_id)
            except Exception as e:
                lock.release()
                return {"status": "fail", "msg": "失败: {}".format(e)}

            lock.release()

            self.app.config['DB'].insert_loginfo(os.environ["USER_NAME"], 'schedulejob', 'resume', job_id, 'success')
            return {"status": "success", "msg": "成功：恢复任务:{}".format(job_id)}

        elif args["method"] == "remove_schedulejob":
            (task_no, user,project,task_name) = (args['task_no'], args['user'],args['project'],args['task_name'])
            job_id = "{}#{}#{}".format(task_no, user, project)

            lock = threading.Lock()
            lock.acquire()

            try:
                scheduler.remove_job(job_id)
            except Exception as e:
                lock.release()
                return {"status": "fail", "msg": "失败: {}".format(e)}

            lock.release()

            res = self.app.config['DB'].runsql("DELETE from schedule_job where user='{}' and project='{}' and task_name='{}';".format(user,project,task_name))

            if res:
                self.app.config['DB'].insert_loginfo(os.environ["USER_NAME"], 'schedulejob', 'remove_schedulejob', job_id, 'success')
            else:
                self.app.config['DB'].insert_loginfo(os.environ["USER_NAME"], 'schedulejob', 'remove_schedulejob', job_id, 'DB Fail')
                return {"status": "fail", "msg": "失败：数据库操作失败:{}".format(job_id)}

            return {"status": "success", "msg": "成功：删除任务成功:{}".format(job_id)}

        elif args["method"] == "delete_allschedulejobs":

            if not self.app.config['USER_NAME'] == 'Admin':
                return {"status": "fail", "msg": "失败:只有Admin可以进行此操作"}

            lock = threading.Lock()
            lock.acquire()

            try:
                scheduler.remove_all_jobs()
            except Exception as e:
                lock.release()
                return {"status": "fail", "msg": "失败: {}".format(e)}
            lock.release()

            res = self.app.config['DB'].runsql("DELETE from schedule_job;")

            if res:
                self.app.config['DB'].insert_loginfo(os.environ["USER_NAME"], 'schedulejob', 'delete_allschedulejobs', 'all', 'success')
            else:
                self.app.config['DB'].insert_loginfo(os.environ["USER_NAME"], 'schedulejob', 'delete_allschedulejobs', "all", 'DB Fail')
                return {"status": "fail", "msg": "失败：数据库操作失败:{}".format('all')}

            return {"status": "success", "msg": "成功：删除任务成功:{}".format('all')}

        elif args["method"] == "add_job2schedule":        # schedul_mng.html "加入调度"
            (task_no, user, project, task_name) = (args['task_no'], args['user'],args['project'],args['task_name'])
            job_id = "{}#{}#{}".format(task_no, user, project)

            job = scheduler.get_job(job_id)
            if job:
                job.resume()
                return {"status": "success", "msg": "任务已存在，开始调度!"}

            res = self.app.config['DB'].runsql("SELECT * from schedule_job where user='{}' and project='{}' and task_name='{}' limit 1;".format(user,project,task_name))
            if not res:
                return {"status": "fail", "msg": "失败:找不到任务!"}
            else:
                (user,project,task_no,task_name,method,schedule_type,year,mon,day,hour,min,sec,week,
                 day_of_week,start_date,end_date,sponsor) = res.fetchone()

            myargs = {'user': user,
                      'project': project,
                      'task_no': task_no,
                      'task_name': task_name,
                      'method': method,
                      'schedule_type': schedule_type,
                      'year': year,
                      'mon': mon,
                      'day': day,
                      'hour': hour,
                      'min': min,
                      'sec': sec,
                      'week': week,
                      'day_of_week': day_of_week,
                      'start_date': start_date,
                      'end_date': end_date,
                      'sponsor': sponsor
                      }

            return add_schedulejob(self.app, scheduler, myargs)

        elif args["method"] == "edit_schedulejob":

            self.log.info("edit_schedulejob, args:{}".format(args))

            splits = args["task_name"].split('_#')  #     project_#task_name@jobid
            if len(splits) != 3:
                return {"status": "fail", "msg": "失败：任务名称的格式错误:{}".format(args["task_name"])}

            (task_no, user, project) = splits
            job_id = "{}#{}#{}".format(task_no, user, project)
            lock = threading.Lock()
            lock.acquire()
            try:
                job = scheduler.get_job(job_id)
                scheduler.remove_job(job_id) if job else None
            except Exception as e:
                lock.release()
                return {"status": "fail", "msg": "失败:清理调度任务失败 {}".format(e)}
            lock.release()

            res = self.app.config['DB'].runsql(''' UPDATE schedule_job set
                                    schedule_type='{}',
                                    year='{}',
                                    mon='{}',
                                    day='{}',
                                    hour='{}',
                                    min='{}',
                                    sec='{}',
                                    week='{}',
                                    day_of_week='{}',
                                    start_date='{}',
                                    end_date='{}' WHERE user='{}' and project='{}' and task_no='{}' ;
                                    '''.format(args['schedule_type'], args['year'], args['mon'], args['day'],
                                               args['hour'], args['min'],
                                               args['sec'], args['week'], args['day_of_week'], args['start_date'],
                                               args['end_date'],
                                               user, project, task_no))

            if res:
                return {"status": "success", "msg": "成功：修改调度信息成功，可以加入调度任务"}
            else:
                return {"status": "fail", "msg": "失败：数据操作失败"}

        elif args["method"] == "add_schedulejob":
            user = os.environ["USER_NAME"]
            self.log.info("add_schedulejob, args:{}".format(args))

            splits = args["task_name"].split('@')  # Project_#03Variables@36
            if len(splits) != 2:
                return {"status": "fail", "msg": "失败：任务名称的格式错误:{}".format(args["task_name"])}

            (task_name, task_no) = splits

            myargs = {'user': user,
                      'project':os.environ["PROJECT_NAME"],
                      'task_no':task_no,
                      'task_name': task_name,
                      'method': args['method'],
                      'schedule_type': args['schedule_type'],
                      'year': args['year'],
                      'mon': args['mon'],
                      'day': args['day'],
                      'hour': args['hour'],
                      'min': args['min'],
                      'sec': args['sec'],
                      'week': args['week'],
                      'day_of_week': args['day_of_week'],
                      'start_date': args['start_date'],
                      'end_date': args['end_date'],
                      'sponsor': 'user'
                      }

            if self.app.config['DB'].add_chedulejob(myargs):
                return add_schedulejob(self.app, scheduler, myargs)
            else:
                return {"status": "fail", "msg": "失败：添加调度任务失败，插入数据库失败。"}

        elif args["method"] == "pause_scheduler":      # pause all job

            if not self.app.config['USER_NAME'] == 'Admin':
                return {"status": "fail", "msg": "失败:只有Admin可以进行此操作"}

            lock = threading.Lock()
            lock.acquire()

            try:
                scheduler.pause()
            except Exception as e:
                lock.release()
                return {"status": "fail", "msg": "失败: {}".format(e)}
            lock.release()

            self.app.config['DB'].insert_loginfo(os.environ["USER_NAME"], 'schedulejob', 'pause_scheduler', "all", 'success')
            return {"status": "success", "msg": "成功：调度器已停止"}

        elif args["method"] == "resume_scheduler":

            if not self.app.config['USER_NAME'] == 'Admin':
                return {"status": "fail", "msg": "失败:只有Admin可以进行此操作"}

            lock = threading.Lock()
            lock.acquire()

            try:
                scheduler.resume()
            except Exception as e:
                lock.release()
                return {"status": "fail", "msg": "失败: {}".format(e)}
            lock.release()

            self.app.config['DB'].insert_loginfo(os.environ["USER_NAME"], 'schedulejob', 'resume_scheduler', "all", 'success')
            return {"status": "success", "msg": "成功：调度器已恢复运行"}

        elif args['method'] == "remove_myschedulejobs":

            lock = threading.Lock()
            lock.acquire()
            try:
                for job in scheduler.get_jobs():
                    (task_no, user, project) = job.id.split('#')
                    if user == self.app.config['USER_NAME']:
                        scheduler.remove_job(job.id)
            except Exception as e:
                lock.release()
                return {"status": "fail", "msg": "Fail: {}".format(e)}
            lock.release()

            res = self.app.config['DB'].runsql("DELETE from schedule_job where user='{}';".format(self.app.config['USER_NAME']))

            if res:
                self.app.config['DB'].insert_loginfo(os.environ["USER_NAME"], 'schedulejob', 'remove_myschedulejobs', 'all',
                                                     'success')
            else:
                self.app.config['DB'].insert_loginfo(os.environ["USER_NAME"], 'schedulejob', 'remove_myschedulejobs', 'all',
                                                     'DB Fail')
                return {"status": "fail", "msg": "数据库操作失败"}

            return {"status": "success", "msg": "删除任务成功"}

        elif args['method'] == "add_monitor":
            self.log.info("添加监控，args：{}".format(args))
            script_conf = args.get("script_conf", None)
            task_no = str(args.get("task_id", None))

            if not script_conf:
                return {"status": "fail", "msg": "cannot find parameter: script_conf"}
            if not task_no:
                return {"status": "fail", "msg": "cannot find parameter: task_id"}

            # (role, ip, port, user, password, home_dir, monitor_item, interval, script, monitor_type)
            splits = script_conf.split('|')
            if len(splits) != 10:
                return {"status": "fail", "msg": "script_conf Error"}

            (role, ip, port, user, password, home_dir, monitor_item,
             interval, script, monitor_type) = splits

            myargs = {'task_no': task_no,
                      'user': ip,
                      'project': monitor_item,
                      'task_name': home_dir + "/dt_scripts/" + script,        # 先在这里组装，后续优化到上层，api 调用处
                      'login_user': user,
                      'login_passwd': password,
                      'login_port': port,
                      'method': args['method'],
                      'schedule_type': 'interval',
                      'year': 0,
                      'mon': 0,
                      'day': 0,
                      'hour': 0,
                      'min': 0,
                      'sec': interval,
                      'week': 0,
                      'day_of_week': 0,
                      'start_date': '',
                      'end_date': '',
                      'sponsor': 'monitor'
                      }

            if self.app.config['DB'].add_chedulejob(myargs):
                return add_monitorjob(scheduler, myargs)
            else:
                return {"status": "fail", "msg": "Insert monitor info to DB failed."}

        elif args['method'] == "delete_monitor":
            self.log.info("删除监控，args：{}".format(args))

            task_no = str(args.get("task_id", None))

            task_num = 0

            lock = threading.Lock()
            lock.acquire()
            try:
                for job in scheduler.get_jobs():
                    (task_id, user, project) = job.id.split('#')
                    if task_id == task_no:
                        scheduler.remove_job(job.id)
                        task_num += 1
            except Exception as e:
                lock.release()
                return {"status": "fail", "msg": "Fail: {}".format(e)}
            lock.release()

            res = self.app.config['DB'].runsql(
                "DELETE from schedule_job where task_no='{}';".format(task_no))

            if res:
                self.app.config['DB'].insert_loginfo(os.environ["USER_NAME"], 'schedulejob', 'del_monitor',
                                                     'all',
                                                     'success')
            else:
                self.app.config['DB'].insert_loginfo(os.environ["USER_NAME"], 'schedulejob', 'del_monitor',
                                                     'all',
                                                     'DB Fail')
                return {"status": "fail", "msg": "数据库操作失败"}

            return {"status": "success", "msg": "删除监控成功", "total": task_num}
        else:
            self.log.error("参数错误： {}".format(args))
            return {"status": "fail", "msg": "参数错误：method 无法识别"}

def get_task_list(app, username, project):
    log = getlogger(__name__)
    # job_path = app.config["AUTO_HOME"] + "/jobs/%s/%s" % (username, project)
    job_path = app.config["OUTPUT_DIR"]
    task = []
    if not exists_path(job_path):
        return {"total": 0, "rows": task}

    fs = os.listdir(job_path)
    jobs = [x for x in fs if x.startswith('20')]      # 任务应该以 年月日开头，避免混入其他的文件或文件夹
    jobs.sort(reverse=True)                                       # 这样会按时间排序

    icons = {
        "running": url_for('static', filename='img/running.gif'),
        "success": url_for('static', filename='img/success.png'),
        "fail": url_for('static', filename='img/fail.png'),
        "exception": url_for('static', filename='img/exception.png')}
    # task = []
    # if exists_path(job_path):
    #     next_build = get_next_build_number(job_path)
    #     if next_build != 0:
    #         # 遍历所有任务结果
    #         # 判断最近一个任务状态
    #
    #
    #         #if exists_path(job_path + "/%s" % (next_build - 1)):
    #         running = False
    #         lock = threading.Lock()
    #         lock.acquire()
    #         remove_robot(app)
    #         for p in app.config["AUTO_ROBOT"]:
    #             if p["name"] == project:
    #                 app.log.info("P name == project :{}".format(project))
    #                 running = True
    #                 break
    #         lock.release()
    #         if running:
    #             task.append(
    #                {
    #                    "status": icons["running"],
    #                    "name": "%s_#%s" % (project, next_build-1),
    #                    "success": "",
    #                    "fail": ""
    #                }
    #             )
    #         last = 1
    #         if running:
    #             last = 2

    for i in jobs:
        output_path = job_path + "/%s" % i
        if exists_path(output_path):
            outxml = output_path + "/output.xml"       # robot output file
            pyres = output_path + "/pytest_res.txt"    # pytest output file

            if exists_path(outxml) and os.stat(outxml).st_size == 0:
                log.info("Job:{} output.xml 大小为0，视为 running")
                driver = get_taskdriver(output_path + "/cmd.txt")
                status = icons["running"]
                task.append({
                    "task_no": i,
                    "status": status,
                    "name": "%s" % i,
                    "driver": driver,
                    "success": "-",
                    "fail": "-",
                    "starttime": "-",
                    "endtime": "-",
                    "elapsedtime": "-",
                    "note": "Running"
                })
                continue
            if exists_path(outxml) and os.stat(outxml).st_size > 0:
                try:
                    driver = get_taskdriver(output_path + "/cmd.txt")
                    suite = ExecutionResult(output_path + "/output.xml").suite
                    stat = suite.statistics
                    name = suite.name
                    if stat.failed != 0:
                        status = icons["fail"]
                    else:
                        status = icons['success']
                    task.append({
                        "task_no": i,
                        "status": status,
                        "name": "<a href='/view_log/%s' target='_blank'>%s@%s</a>" % (i, name ,i),
                        "driver": driver,
                        "success": stat.passed,
                        "fail": stat.failed,
                        "starttime": suite.starttime,
                        "endtime": suite.endtime,
                        "elapsedtime": suite.elapsedtime,
                        "note": "<a href='/view_report/%s' target='_blank'>%s_report</a>" % (i, name)
                    })
                except:
                    status = icons["exception"]
                    task.append({
                        "task_no": i,
                        "status": status,
                        "name": "%s" % i,
                        "driver":driver,
                        "success": "-",
                        "fail": "-",
                        "starttime": "-",
                        "endtime": "-",
                        "elapsedtime": "-",
                        "note": "Abnormal"
                    })
                continue

            if exists_path(pyres) and os.stat(pyres).st_size == 0:
                driver = get_taskdriver(job_path + "/%s/cmd.txt" % i)
                status = icons["running"]
                task.append({
                    "task_no": i,
                    "status": status,
                    "name": "%s" % i,
                    "driver": driver,
                    "success": "-",
                    "fail": "-",
                    "starttime": "-",
                    "endtime": "-",
                    "elapsedtime": "-",
                    "note": "Abnormal"
                })
                continue

            if exists_path(pyres) and os.stat(pyres).st_size > 0:    # pytest 的输出是 pytest_res.txt
                driver = get_taskdriver(job_path + "/%s/cmd.txt" % i)
                result = {}
                with open(pyres, 'r') as rf:
                    result = json.load(rf)
                success = result["success"]
                fail = result["fail"]
                elapsedtime = result["duration"]
                source = result["source"]
                name = os.path.basename(source)

                if result["fail"] > 0:
                    status = icons["fail"]
                else:
                    status = icons["success"]
                task.append({
                    "task_no": i,
                    "status": status,
                    "name": "<a href='/view_log/%s' target='_blank'>%s@%s</a>" % (i, name, i),
                    "driver": driver,
                    "success": success,
                    "fail": fail,
                    "starttime": "unknown",
                    "endtime": "unknown",
                    "elapsedtime": elapsedtime,
                    "note": "<a href='/view_report/%s' target='_blank'>%s_report</a>" % (i, source)
                })
                continue

            task.append({
                "task_no": i,
                "status": icons["exception"],
                "name": "%s" % i,
                "driver": "unknown",
                "success": "-",
                "fail": "-",
                "starttime": "-",
                "endtime": "-",
                "elapsedtime": "-",
                "note": "Empty dir"
            })

    return {"total": len(task), "rows": task}

def get_schedulejob_list(app, args):

    joblist = []
    res = app.config['DB'].runsql('SELECT * from schedule_job;')
    for i in res:
        (user,project,task_no,task_name,method,schedule_type,
         year,mon,day,hour,min,sec,week,
         day_of_week,start_date,end_date,sponsor) = i

        joblist.append([user,project,task_name,task_no,method,schedule_type,
         year,mon,day,hour,min,sec,week,
         day_of_week,start_date,end_date,sponsor,'unScheduled',''])  #job_id = "{}#{}#{}".format(user,project,task_name)

    jobs = scheduler.get_jobs()

    jobids = [x.id for x in jobs]

    for j in joblist:
        id = j[3]+'#'+j[0]+'#'+j[1]
        if id in jobids:
            jb = scheduler.get_job(id)
            j[18] = jb.next_run_time
            j[17] = 'running' if j[18] is not None else 'pause'
            jobids.remove(id)

    for i in jobids:
        (t,u,p) = i.split('#')
        jb = scheduler.get_job(i)
        joblist.append([u,p,t,'','','','','','','','','','','','','','',
                      'running' if jb.next_run_time is not None else 'pause', jb.next_run_time])

    icons = {
        "pause": url_for('static', filename='img/unknown.png'),
        "running": url_for('static', filename='img/success.png'),
        "unScheduled": url_for('static', filename='img/fail.png'),
        "schedulerPaused": url_for('static', filename='img/innormal.png')
    }

    rlist = []
    for j in joblist:

        if j[17] == 'running':
            status = icons['running']
        elif j[17] == 'pause':
            status = icons['pause']
        else:
            status = icons['unScheduled']

        if scheduler.state == 2:
            status = icons['schedulerPaused']

        rlist.append(
            {
                "task_no": j[3],
                "user": j[0],
                "project": j[1],
                "task_name": j[2],
                #"method": j[4],
                "schedule_type": j[5],
                "year": j[6],
                "mon": j[7],
                "day": j[8],
                "hour": j[9],
                "min": j[10],
                "sec": j[11],
                "week": j[12],
                "day_of_week": j[13],
                "start_date": j[14],
                "end_date": j[15],
                "sponsor": j[16],
                "status": status,
                "next_time": str(j[18])
            }
        )
    return {"total": 1, "rows": rlist}

# def get_last_pass(job_path):
#     passed = "无"
#     passed_path = job_path + "lastPassed"
#     if exists_path(passed_path):
#         f = codecs.open(passed_path, "r", "utf-8")
#
#         passed = f.read()
#
#         f.close()
#
#     return passed


# def get_last_fail(job_path):
#     fail = "无"
#     fail_path = job_path + "lastFail"
#     if exists_path(fail_path):
#         f = codecs.open(fail_path, "r", "utf-8")
#
#         fail = f.read()
#
#         f.close()
#
#     return fail


def get_next_build_number(job_path):
    next_build_number = 1
    next_path = job_path + "/nextBuildNumber"
    if exists_path(next_path):
        f = codecs.open(next_path, "r", "utf-8")

        next_build_number = int(f.read())

        f.close()

    return next_build_number


def get_next_time(app, name):
    job = scheduler.get_job("%s_%s" % (os.environ["USER_NAME"], name))
    if job:
        to_zone = tz.gettz("CST")
        return job.next_run_time.astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S")
    else:
        return "-"


def edit_cron(app, name, cron):
    user_path = app.config["AUTO_HOME"] + "/users/" + os.environ["USER_NAME"]
    if os.path.exists(user_path):
        config = json.load(codecs.open(user_path + '/config.json', 'r', 'utf-8'))
        index = 0
        for p in config["data"]:
            if p["name"] == name:
                config["data"][index]["cron"] = cron
                break
            index += 1

        json.dump(config, codecs.open(user_path + '/config.json', 'w', 'utf-8'))

        return True

    return False

def get_taskdriver(cmdfile):
    if not os.path.exists(cmdfile):
        return 'Unknown'
    else:
        with open(cmdfile, 'r') as f:
            ln = f.readline().strip()
            splits = ln.split('|')
            return splits[0] if len(splits) > 1 else 'Unknown'

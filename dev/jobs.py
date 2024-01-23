#!/usr/bin/python3 -u

from builtins import open, print
import subprocess, os, sys, time, signal, enum
from collections import deque
import datetime

class JobStatus(enum.Enum):
  PENDING = enum.auto()
  RUNNING = enum.auto()
  SUCCESS = enum.auto()
  FAIL = enum.auto()
  ABORT = enum.auto()
  CANCEL = enum.auto()

class JobType(enum.Enum):
  NORMAL_JOB = enum.auto() # 正常job
  ERROR_JOB = enum.auto() # 正常job失败时触发该job

class Jobs:
  def __init__(self, log_dir, immediately_abort = True):
    if not os.path.exists(log_dir):
      os.makedirs(log_dir)
    self.log_dir = log_dir
    self.jobs = {}
    self.fail_job = None
    self.error_jobs = []
    self.immediately_abort = immediately_abort
    self.stop_job = False
    signal.signal(signal.SIGINT, lambda signum, frame: self.stop_jobs())
  
  def add_job(self, name, command, deps = [], type = JobType.NORMAL_JOB, status = JobStatus.PENDING):
    ignore_log = name.startswith("@")
    if ignore_log:
      name = name[1:]

    if name in self.jobs:
      print(f"Error: Duplicate job name {name}")
      sys.exit(1)

    log_file_name = None
    if not ignore_log:
      log_file_name = f"{self.log_dir}/{name}.log"
    self.jobs[name] = {
      "name": name,
      "log_file_name": log_file_name,
      "log_file": None,
      "log_file_read": None,
      "last_lines": deque([], 100),
      "command": command,
      "deps": deps,
      "status": status, # pending, running, finish, cancel, abort
      "type": type,
    }
  def print_stdout(self, job):
    log_file = job["log_file_read"]
    if not log_file:
        return
    try:
      for line in log_file.readlines():
        line = "job(" + job["name"] + "): " + line.strip()
        job["last_lines"].append(line)
        print(line)
    except:
        pass

  def has_unfinish_job (self, type):
    for name, job in self.jobs.items():
      if job["type"] == type and (job["status"] == JobStatus.PENDING or job["status"] == JobStatus.RUNNING):
        return True
    return False

  def print_jobs_status(self, success):
    print("Jobs stats:")
    for name, job in self.jobs.items():
      if success and job["type"] == JobType.ERROR_JOB:
        continue
      status = job["status"]
      command = job["command"]
      str = f"  {name}: status: {status}"
      if "start_time" in job and "end_time" in job:
        start_time = job["start_time"]
        diff_time = job["end_time"] - start_time
        str += f", time: {diff_time}, start_time: {start_time}"
      str += f", cmd: {command}"
      print(str)

  def run_jobs(self, current_type):
    has_fail = False
    while self.has_unfinish_job(current_type):
      for name, job in self.jobs.items():
        status = job["status"]
        type = job["type"]
        if type != current_type:
          continue
        if status == JobStatus.SUCCESS or \
           status == JobStatus.FAIL or \
           status == JobStatus.ABORT or \
           status == JobStatus.CANCEL:
          continue
        elif status == JobStatus.PENDING:
          deps_ready = True
          is_cancel = False
          for dep in job["deps"]:
            if dep not in self.jobs:
              print(f"Error: Does not exist dependence job {name}")
              sys.exit(1)
            dep_status = self.jobs[dep]["status"]
            if dep_status == JobStatus.PENDING or dep_status == JobStatus.RUNNING:
              deps_ready = False
            elif dep_status == JobStatus.FAIL or dep_status == JobStatus.ABORT or dep_status == JobStatus.CANCEL:
              is_cancel = True
              break
          if is_cancel:
            job["status"] = JobStatus.CANCEL
            print(f"Cancel job({name})")
            continue
          elif not deps_ready:
            # wait
            continue
          else:
            # start to running
            if job["log_file_name"]:
                job["log_file"] = open(job["log_file_name"], "w")
                job["log_file_read"] = open(job["log_file_name"], "r")
            job["process"] = subprocess.Popen(job["command"], stdout=job["log_file"], stderr=job["log_file"], universal_newlines=True, env=os.environ, shell=True, start_new_session=True)
            job["status"] = JobStatus.RUNNING
            job["start_time"] = datetime.datetime.now()
            print(f"Start job({name})")
            print(f'cmd: {job["command"]}')

        # RUNNING Jobs
        assert job["status"] == JobStatus.RUNNING
        if self.stop_job:
          self.abort_jobs()
          return True
        process = job["process"]
        self.print_stdout(job)
        return_code = process.poll()
        if return_code is not None:
          self.print_stdout(job)
          job["log_file"] and job["log_file"].close()
          job["log_file_read"] and job["log_file_read"].close()
          job["end_time"] = datetime.datetime.now()
          if return_code != 0:
            job["status"] = JobStatus.FAIL
            self.error_jobs.append({
              "header": f"job({name}): failed with code {return_code}.",
              "last_lines": job["last_lines"]
            })
            print(f"Failed job({name})")
            has_fail = True
            if self.immediately_abort:
              self.abort_jobs()
              return has_fail
          else:
            job["status"] = JobStatus.SUCCESS
            print(f"Success job({name})")
    return has_fail

  def abort_jobs(self):
    for name, job in self.jobs.items():
      if job["status"] == JobStatus.PENDING:
        job["status"] = JobStatus.CANCEL
        job["end_time"] = datetime.datetime.now()
        print(f"Cancel job({name})")
      elif job["status"] == JobStatus.RUNNING:
        job["status"] = JobStatus.ABORT
        job["end_time"] = datetime.datetime.now()
        print(f"Abort job({name})")
        os.killpg(job["process"].pid, signal.SIGKILL)

  def stop_jobs(self):
    self.stop_job = True

  def start_jobs(self):
    has_fail = self.run_jobs(JobType.NORMAL_JOB)
    if has_fail:
      has_fail2 = self.run_jobs(JobType.ERROR_JOB)

    if len(self.error_jobs) > 0:
      for err_job in self.error_jobs:
        print(err_job["header"] + " last lines log:")
        for line in err_job["last_lines"]:
          print("    " + line)
      for err_job in self.error_jobs:
        print(err_job["header"])
      self.print_jobs_status(False)
      print("all jobs finish with errors.")
      print(f"logs save to {self.log_dir}")
      sys.exit(1)
    else:
      self.print_jobs_status(True)
      print("all jobs finish.")
      print(f"logs save to {self.log_dir}")

# demo
if __name__ == "__main__":
  jobs = Jobs("./test_log")
  # @表示不记录日志
  jobs.add_job("@job1", "sleep 1 && echo xxx")
  jobs.add_job("job2", "sleep 2 && echo xxx", ["job1"])
  jobs.add_job("job3", "sleep 3 && exit 0")
  jobs.start_jobs()

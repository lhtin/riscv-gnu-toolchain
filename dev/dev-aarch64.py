#!/usr/bin/env python3

import argparse
import sys
import subprocess
import os
from datetime import datetime
from jobs import Jobs

work_dir = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(
    description="For GCC developer", add_help=False)
parser.add_argument('--jobs', type=str, required=False,
                    default="1", help="allow number of parallel tasks")
parser.add_argument('--suffix', type=str, default="",
                    required=False, help="suffix of build dir")
parser.add_argument('--release', action="store_true", default=False)
parser.add_argument('--src-dir', type=str, default=".", required=False)
parser.add_argument('--gcc-src', type=str, default="gcc", required=True)
parser.add_argument('--test', action="store_true", default=False)
parser.add_argument('--only-test', action="store_true", default=False)

args = parser.parse_args()

src_dir = os.path.abspath(args.src_dir)
gcc_src = os.path.join(src_dir, args.gcc_src)
cflags = "-O2" if args.release else "-O0 -g3"
build_type = "release" if args.release else "debug"
prefix_name = f"aarch64-{build_type}-{args.gcc_src}"
if args.suffix:
  prefix_name = prefix_name + f"-{args.suffix}"
build_dir = os.path.join(work_dir, f"build/{prefix_name}")
prefix_dir = os.path.join(work_dir, f"build/{prefix_name}/install")
make_file = os.path.join(work_dir, "aarch64-cross.mk")

start_time = datetime.now()

MAP = f'BUILD_DIR={build_dir} \
PREFIX_DIR={prefix_dir} \
SRC_DIR={src_dir} \
GCC_SRC_DIR={gcc_src} \
QEMU_SRC_DIR={os.path.join(src_dir, "qemu-8.2.1")}'

jobs = Jobs(build_dir)

if args.test:
  if args.only_test:
    jobs.add_job("test", f'make -f {make_file} test CFLAGS="{cflags}" {MAP} -j{args.jobs}')
  else:
    jobs.add_job("@clean", f"rm -rf {prefix_dir} {build_dir} && mkdir -p {build_dir}")
    jobs.add_job("build", f'make -f {make_file} build CFLAGS="{cflags}" {MAP} -j{args.jobs}', ["clean"])
    jobs.add_job("test", f'make -f {make_file} test CFLAGS="{cflags}" {MAP} -j{args.jobs}', ["build"])
else:
  jobs.add_job("@clean", f"rm -rf {prefix_dir} {build_dir} && mkdir -p {build_dir}")
  jobs.add_job("build", f'make -f {make_file} build CFLAGS="{cflags}" {MAP} -j{args.jobs}', ["clean"])


jobs.start_jobs()

print("Total time:", datetime.now() - start_time)


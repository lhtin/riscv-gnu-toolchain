#!/usr/bin/env python3

import argparse
import sys
import subprocess
import os
from datetime import datetime

def run_sync(cmd):
  print(cmd)
  process = subprocess.Popen(cmd, shell=True, start_new_session=True)
  try:
    process.wait()
  except KeyboardInterrupt:
    print(f"Kill subprocess {process.pid} and it's children.")
    os.system(f"pkill --session {process.pid}")
    sys.exit(1)

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
parser.add_argument('--bootstrap', action="store_true", default=False)
parser.add_argument('--test', action="store_true", default=False)

args = parser.parse_args()

src_dir = os.path.abspath(args.src_dir)
gcc_src = os.path.join(src_dir, args.gcc_src)
cflags = "-O2" if args.release else "-O0 -g3"
build_type = "release" if args.release else "debug"
prefix_name = f"x64-{build_type}-{args.gcc_src}-{'bootstrap' if args.bootstrap else 'simple'}"
if args.suffix:
  prefix_name = prefix_name + f"-{args.suffix}"
build_dir = os.path.join(work_dir, f"build/{prefix_name}")
prefix_dir = os.path.join(work_dir, f"build/{prefix_name}/install")

make_file = os.path.join(work_dir, "x64-simple.mk")
log_file = f"{build_dir}/build.log"

run_sync(f"rm -rf {build_dir} {prefix_dir} && mkdir -p {build_dir}")
start_time = datetime.now()
run_sync(f'make -f {make_file} GCC_SRC_DIR={gcc_src} CFLAGS="{cflags}" BUILD_DIR={build_dir} PREFIX_DIR={prefix_dir} -j{args.jobs} 2>&1 | tee {log_file}')
if args.test:
        os.chdir(f"{build_dir}/build-gcc")
        run_sync(f"make check-gcc -j{args.jobs}")
print("Total time:", datetime.now() - start_time)

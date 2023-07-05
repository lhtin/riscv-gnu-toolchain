#!/usr/bin/env python3

import argparse
import sys
import subprocess
import os

def run_sync (cmd):
  print(cmd)
  process = subprocess.Popen(cmd, shell=True, start_new_session=True)
  try:
    process.wait()
  except KeyboardInterrupt:
    print(f"Kill subprocess {process.pid} and it's children.")
    os.system(f"pkill --session {process.pid}")
    sys.exit(1)

parser = argparse.ArgumentParser(description="For GCC developer.", add_help=False)
parser.add_argument('--with-arch', type=str, required=True, help='default -march')
parser.add_argument('--with-abi', type=str, required=False, help="default -mabi")
parser.add_argument('--prefix-name', type=str, required=False, help="Prefix Name")
parser.add_argument('--help', action="store_true", default=False)
args, unknown = parser.parse_known_args()

if args.help:
  run_sync ("./configure --help")
  sys.exit(0)

extra_options = ' '.join(unknown)
if extra_options:
  print(f"Pass extra options `{extra_options}` to configure")

work_dir = os.path.dirname(os.path.realpath(__file__))

prefix_name = f"{args.prefix_name}-{args.with_arch}-{args.with_abi}"
build_dir = os.path.join(work_dir, f"build-{prefix_name}")
prefix_dir = os.path.join(work_dir, f"install-{prefix_name}")

print(f"build dir: {build_dir}")
print(f"prefix dir: {prefix_dir}")
run_sync (f"rm -rf {build_dir} {prefix_dir} && mkdir {build_dir}")
os.chdir(build_dir)
run_sync (f"../configure --prefix={prefix_dir} --with-arch={args.with_arch} --with-abi={args.with_abi} {extra_options} 2>&1 | tee confg.log")
run_sync (f"GCC_EXTRA_CONFIGURE_FLAGS='CFLAGS=\"-O0 -g3\" CXXFLAGS=\"-O0 -g3\"' make -j 2>&1 | tee build.log")

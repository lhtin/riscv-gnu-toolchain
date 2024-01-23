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


parser = argparse.ArgumentParser(
    description="For GCC developer", add_help=False)
parser.add_argument('--with-arch', type=str, required=True, help='set -march')
parser.add_argument('--with-abi', type=str, required=True, help="set -mabi")
parser.add_argument('--with-cmodel', type=str, required=False,
                    default="medany", help="default -cmodel=medany")
parser.add_argument('--with-sim', type=str, required=True, help="qemu, spike")
parser.add_argument('--libc', type=str, required=False,
                    default="linux", help="choose use newlib, linux, musl")
parser.add_argument('--suffix', type=str, default="",
                    required=False, help="suffix of build dir")
parser.add_argument('--jobs', type=str, required=False,
                    default="", help="allow number of parallel tasks")
parser.add_argument('--tags', action="store_true",
                    default=False, help="gen tags of source")
parser.add_argument('--help', action="store_true", default=False)
parser.add_argument('--release', action="store_true", default=False)
parser.add_argument('--dynamic', action="store_true", default=False)
parser.add_argument('--src-dir', type=str, default=".", required=False)
parser.add_argument('--gcc-src', type=str, default="gcc", required=False)
parser.add_argument('--test', action="store_true", default=False)

args, unknown = parser.parse_known_args()
work_dir = os.path.dirname(os.path.realpath(__file__))
configure_file = os.path.join(work_dir, "../configure")

if args.help:
  parser.print_help()
  print("\n================================================================================\n")
  run_sync(f"{configure_file} --help")
  sys.exit(0)

extra_options = ' '.join(unknown)
if extra_options:
  print(f"Pass extra options `{extra_options}` to configure")


build_type = "release" if args.release else "debug"
prefix_name = f"{build_type}-{args.gcc_src}-{args.with_arch}-{args.with_abi}-{args.with_cmodel}-{args.libc}-{args.with_sim}"
if args.suffix:
  prefix_name = prefix_name + f"-{args.suffix}"
build_dir = os.path.join(work_dir, f"build/{prefix_name}")
prefix_dir = os.path.join(work_dir, f"build/{prefix_name}/install")

if args.tags:
  run_sync(f'ctags --fields=+iaS --extras=+q --exclude="gcc/gcc/testsuite/*" --exclude="gcc/gcc/config/*" --exclude-exception="gcc/gcc/config/riscv/*" --append=no --recurse --totals=yes gcc/gcc || true')

src_dir = os.path.abspath(args.src_dir)
with_src = f"--with-binutils-src={src_dir}/binutils \
--with-gcc-src={src_dir}/{args.gcc_src} \
--with-gdb-src={src_dir}/gdb \
--with-glibc-src={src_dir}/glibc \
--with-llvm-src={src_dir}/llvm \
--with-musl-src={src_dir}/musl \
--with-newlib-src={src_dir}/newlib \
--with-pk-src={src_dir}/pk \
--with-qemu-src={src_dir}/qemu \
--with-spike-src={src_dir}/spike"
build_flags = "-O2" if args.release else "-O0 -g3"
ld_flags = "" if args.dynamic else "-static"

print(f"gcc src: {src_dir}/{args.gcc_src}")
print(f"build dir: {build_dir}")
print(f"prefix dir: {prefix_dir}")

run_sync(f"rm -rf {build_dir} {prefix_dir} && mkdir -p {build_dir}")
os.chdir(build_dir)
start_time = datetime.now()
run_sync(f"{configure_file} {with_src} \
--prefix={prefix_dir} \
--with-arch={args.with_arch} \
--with-abi={args.with_abi} \
--with-cmodel={args.with_cmodel} \
--with-sim={args.with_sim} \
--with-gcc-extra-configure-flags='CFLAGS=\"{build_flags}\" CXXFLAGS=\"{build_flags}\" LDFLAGS=\"{ld_flags}\"' \
{extra_options} 2>&1 | tee config.log")
run_sync(f"make {args.libc} -j{args.jobs} 2>&1 | tee build.log")
if args.test:
        run_sync(f"make report-{args.libc} -j{args.jobs} 2>&1 | tee test.log")
print("Total time:", datetime.now() - start_time)

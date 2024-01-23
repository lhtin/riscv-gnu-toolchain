#!python3

import argparse, subprocess, sys, os

parser = argparse.ArgumentParser(description='Check gcc testsuite result.')
parser.add_argument ("--golden_dir", type=str, required=True)
parser.add_argument ("--test_dir", type=str, required=True)
parser.add_argument ("--tool-list", nargs="+", required=True, help="gcc,g++,gfortran,objc,...")

args = parser.parse_args()

work_dir = os.path.dirname(os.path.realpath(__file__))

cmd = '''
python3 {work_dir}/check-single.py --golden_file {golden_dir}/{tool}/{tool}.sum --summary_file {test_dir}/{tool}/{tool}.sum
'''

has_fail = False

def run (cmd):
  global has_fail
  try:
    subprocess.run(cmd, check=True, shell=True, stderr=subprocess.STDOUT)
  except Exception:
    has_fail = True

for tool in args.tool_list:
  sum_file = f"{args.test_dir}/{tool}/{tool}.sum"
  if os.path.isfile(sum_file):
    check_cmd = cmd.format (**{"golden_dir": args.golden_dir, "test_dir": args.test_dir, "tool": tool, "work_dir": work_dir})
    print(check_cmd)
    run(check_cmd)
  else:
    print(f"Cannot find summary {sum_file}")

if has_fail:
  print("Finish with FAILED.")
  sys.exit (1)

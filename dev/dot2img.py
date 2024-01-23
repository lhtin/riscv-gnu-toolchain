#!python3

import subprocess, sys, os, argparse, re

def run_sync (cmd):
  print(f"Run {cmd}")
  process = subprocess.Popen(cmd, shell=True, start_new_session=True)
  try:
    process.wait()
  except KeyboardInterrupt:
    print(f"Kill subprocess {process.pid} and it's children.")
    os.system(f"pkill --session {process.pid}")
    sys.exit(1)


parser = argparse.ArgumentParser()
parser.add_argument('--dot', type=str, required=True, help='.dot file')
parser.add_argument('--type', type=str, default="png",
                    help='output format (png, pdf, ...), default is png')
args = parser.parse_args()

temps = os.path.splitext(args.dot)
new_dot_path = f"{temps[0]}.2{temps[1]}"
new_dot_file = open (new_dot_path, "w")
with open (args.dot, "r") as dot_file:
  in_block = False
  for line in dot_file.readlines():
    if "label=\"{" in line:
      in_block = True
      new_dot_file.writelines([line])
    elif "}\"];" in line:
      in_block = False
      new_dot_file.writelines([line])
    elif in_block:
       line = re.sub(r"( |\"|\<|\>|\*|\{|\})", r"\\\1", line)
       line = re.sub(r"\n", r"\\l\\\n", line)
       new_dot_file.writelines([line])
    else:
      new_dot_file.writelines([line])

print(new_dot_path)
new_dot_file.close()
run_sync (f"dot -T{args.type} -o {temps[0]}.{args.type} {new_dot_path}")
      

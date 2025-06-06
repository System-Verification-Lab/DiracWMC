
from subprocess import PIPE, Popen, TimeoutExpired
from tempfile import NamedTemporaryFile
import sys

TIMEOUT = 15
SRC_FOLDER = "/usr/src/app/TensorOrder"

# If no command line arguments are given, stdin is read
if len(sys.argv) > 1:
    inputs = sys.argv[1:]
else:
    inputs = [sys.stdin.read()]

def run_on_input(inp: str) -> "str | None":
    """ Run the solver on the given input and return result string, or None if
        the operation failed """
    temp_file = NamedTemporaryFile()
    with open(temp_file.name, "w") as f:
        f.write(inp)
    infile = open(temp_file.name, "r")
    p = Popen(["python", "./src/tensororder.py", "--planner=factor-Flow",
    "--weights=cachet", f"--timeout={TIMEOUT}"], cwd=SRC_FOLDER, stdout=PIPE,
    stdin=infile, stderr=PIPE)
    try:
        output, _ = p.communicate(timeout=TIMEOUT)
    except TimeoutExpired:
        return None
    return output.decode("utf-8")

output: "list[str]" = []
for inp in inputs:
    result = run_on_input(inp)
    if result is None:
        print("ERR")
        exit(1)
    output.append(result)
for out in output:
    print(out)
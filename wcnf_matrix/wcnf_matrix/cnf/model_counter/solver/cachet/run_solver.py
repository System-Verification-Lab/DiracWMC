
from subprocess import PIPE, Popen, TimeoutExpired
from tempfile import NamedTemporaryFile
import sys
from time import time

TIMEOUT = 15
SRC_FOLDER = "/usr/src/app/cachet"

# If no command line arguments are given, stdin is read
if len(sys.argv) > 1:
    inputs = sys.argv[1:]
else:
    inputs = [sys.stdin.read()]

for i, inp in enumerate(inputs):
    print(f"Input #{i}: {inp}")

def run_on_input(inp: str) -> str | None:
    """ Run the solver on the given input and return result string, or None if
        the operation failed """
    temp_file = NamedTemporaryFile()
    with open(temp_file.name, "w") as f:
        f.write(inp)
    p = Popen(["./cachet", temp_file.name], cwd=SRC_FOLDER, stdout=PIPE)
    try:
        start = time()
        output, _ = p.communicate(timeout=TIMEOUT)
        end = time()
    except TimeoutExpired:
        return None
    return output.decode("utf-8") + "\nRUNTIME: " + str(end - start)

output: list[str] = []
for inp in inputs:
    result = run_on_input(inp)
    if result is None:
        print("ERR")
        exit(1)
    output.append(result)
for out in output:
    print(out)
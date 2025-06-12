
from subprocess import PIPE, Popen, TimeoutExpired
from tempfile import NamedTemporaryFile
import sys
import json

TIMEOUT = 15
SRC_FOLDER = "/usr/src/app/DPMC"

inputs: list[str] = json.loads(sys.stdin.read())["problems"]

def run_on_input(inp: str) -> str | None:
    """ Run the solver on the given input and return result string, or None if
        the operation failed """
    temp_file = NamedTemporaryFile()
    with open(temp_file.name, "w") as f:
        f.write(inp)
    infile = open(temp_file.name, "r")
    p1 = Popen(["./lg/build/lg", "./lg/solvers/flow-cutter-pace17/"
    "flow_cutter_pace17 -p 100"], cwd=SRC_FOLDER, stdout=PIPE, stdin=infile)
    p2 = Popen(["./dmc/dmc", f"--cf={temp_file.name}"], cwd=SRC_FOLDER, stdout=PIPE,
    stdin=p1.stdout)
    try:
        output, _ = p2.communicate(timeout=TIMEOUT)
    except TimeoutExpired:
        return None
    return output.decode("utf-8")

results = {"results": [], "inputs": inputs}
for inp in inputs:
    result = run_on_input(inp)
    if result is None:
        results["results"].append("ERR")
    else:
        results["results"].append(result)
print(json.dumps(results))
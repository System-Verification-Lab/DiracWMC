
def replace_in_file(filename: str, find: str, replace: str):
    with open(filename, "r") as f:
        content = f.read()
    with open(filename, "w") as f:
        f.write(content.replace(find, replace))

replace_in_file("./solvers/flow-cutter-pace17/src/list_graph.h",
"#include <tuple>", "#include <tuple>\n#include <string>")
replace_in_file("./src/tensor_network/tensor_apis/numpy_apis.py",
"self._numpy.object", "object")
replace_in_file("./src/tensororder.py",
"if jax_tensordot is not \"tensordot\":", "if jax_tensordot != \"tensordot\":")
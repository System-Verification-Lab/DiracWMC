
import importlib
import sys

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <test_name>")
    exit(1)

experiment_name = sys.argv[1]
experiment = importlib.import_module(f"app.experiments.{experiment_name}")
experiment.run()
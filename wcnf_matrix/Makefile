
all:
	pip install .

build:
	pip install twine build
	python -m build

install:
	pip install .

test: install
	pytest -s

clean:
	rm -rf build
	rm -rf wcnf_matrix.egg-info
	find . | grep -E "(/__pycache__$$|\.pyc$$|\.pyo$$)" | xargs rm -rf
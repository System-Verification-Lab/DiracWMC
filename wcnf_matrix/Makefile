
all:
	pip install .

build:
	pip install twine build
	python -m build

install:
	pip install .

test: install
	pytest -s
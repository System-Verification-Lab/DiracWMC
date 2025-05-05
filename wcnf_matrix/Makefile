
all:
	pip install twine build
	python -m build

install:
	pip install .

test: install
	pytest -s

solvers/DPMC:
	mkdir -p solvers; \
	cd solvers; \
	git clone --recursive https://github.com/vardigroup/DPMC; \
	cd DPMC; \
	cd lg; \
	make; \
	cd solvers/flow-cutter-pace17; \
	make; \
	cd ../../../dmc; \
	make dmc
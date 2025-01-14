
all:

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
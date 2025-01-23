
# Installation and using the Cachet solver

Below are instructions for installing and using the Cachet solver. The installation requires Linux. For this g++ and make have to be installed. C++98 is used for compilation.

## Installation and setup

Check the `/usr/src` folder for a `linux-headers-*` folder. If it does not exist (this is probably the case on WSL) add it by using:
```bash
apt-get install linux-headers-generic
```
Find out which linux headers folder has been created by looking in `/usr/src` folder. Now create a link at `/usr/include/linux/sys.h` by using: (fill in the headers name)
```bash
ln -s /usr/src/linux-headers-[headers-name]/include/linux/sys.h /usr/include/linux/sys.h
```
Then download the Cachet source code from [here](https://henrykautz.com/Cachet/). Place the `cachet` folder (containing all of the `.cpp` and `.h` files) in the `solvers` folder. Now navigate to this `cachet` folder in the console. Before compiling, a couple things need to be changed:

- Go to the `hash.h` file an uncomment the lines `#include <linux/sys.h>` and  `#include <sys/sysinfo.h>` at the top of the file.
- Go the the `Makefile` and add at the end of the line starting with `CFLAGS` the flag `-std=c++98` (after `-DNDEBUG`). This ensures the correct compiler is used.

After this, the source code can be built using `make`.

## Usage

Note that the input files of Cachet are in a different format from DPMC (despite having the same extension `.cnf`). Run Cachet using
```bash
./cachet [cnf-file]
```

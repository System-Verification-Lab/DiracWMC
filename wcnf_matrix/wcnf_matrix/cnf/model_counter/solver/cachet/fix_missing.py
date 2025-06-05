
# Fix hash.h file
with open("./cachet/hash.h", "r") as f:
    content = f.read()
content = content.replace("//#include <linux/sys.h>", "#include <linux/sys.h>")
content = content.replace("//#include <sys/sysinfo.h>",
"#include <sys/sysinfo.h>")
with open("./cachet/hash.h", "w") as f:
    f.write(content)

# Fix Makefile
with open("./cachet/Makefile", "r") as f:
    content = f.read()
content = content.replace("CFLAGS = -static -O6 -DNDEBUG #-pg", "CFLAGS = "
"-static -O6 -DNDEBUG -std=c++98 #-pg")
with open("./cachet/Makefile", "w") as f:
    f.write(content)
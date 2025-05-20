
import sys

_, filename, line = sys.argv
with open(filename, "r") as f:
    content = f.read()
index = content.rfind("#include")
if index == -1:
    raise LookupError("Could not found includes in given file")
content = content[:index] + line + "\n" + content[index:]
with open(filename, "w") as f:
    f.write(content)
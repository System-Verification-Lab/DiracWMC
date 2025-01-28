
from typing import Any
from datetime import datetime

STAT_PADDING = 35

class ConsoleColor:
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    GREY = "\033[90m"
    CLEAR = "\033[0m"

def log_info(content: Any = ""):
    """ Show an info message """
    date = datetime.now().strftime("%H:%M:%S.%f")
    print(f"{ConsoleColor.GREY}[{date}] {content}{ConsoleColor.CLEAR}")

def log_stat(name: str = "", content: Any = "N/A"):
    """ Show a statistic with the given name """
    if name == "":
        return
    print(ConsoleColor.CYAN + (name + ":").ljust(STAT_PADDING) + " " +
    ConsoleColor.CLEAR + str(content))
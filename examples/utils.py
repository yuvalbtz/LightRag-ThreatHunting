import csv
from enum import Enum
import json
import sys
import types
from typing import Any, Dict, List


# Create a new module
utils_module = types.ModuleType('utils')

async def read_csv(file_path: str) -> List[Dict[str, Any]]:
    """Reads a CSV file and returns a list of dictionaries."""
    flows = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
             flows.append({
                "Flow ID": row["Flow ID"],
                "Src IP": row["Src IP"],
                "Dst IP": row["Dst IP"],
                "Timestamp": row["Timestamp"]
            })
    return flows


async def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, mode='r') as file:
        return json.load(file)
    

class Colors(Enum):
    SUCCESS = '\033[1;32m'  # Bold green text
    WARNING = '\033[1;43m'  # Bold text with yellow background
    ERROR = '\033[1;41m'    # Bold text with red background
    RESET = '\033[0m'       # Reset all formatting
    
def printTextColor(color: Colors, text: str):
    print(f"{color.value}[{color.name}] {text}{Colors.RESET.value}")
    

# Add them to the module
utils_module.Colors = Colors
utils_module.printTextColor = printTextColor

# Add the module to sys.modules
sys.modules['utils'] = utils_module
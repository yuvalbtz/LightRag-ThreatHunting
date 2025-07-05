import csv
from enum import Enum
import json
import os
import sys
import types
from typing import Any, Dict, List

# Create a new module


async def read_csv(file_path: str) -> List[Dict[str, Any]]:
    """Reads a CSV file and returns a list of dictionaries."""
    flows = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            flows.append(
                {
                    "Flow ID": row["Flow ID"],
                    "Src IP": row["Src IP"],
                    "Dst IP": row["Dst IP"],
                    "Timestamp": row["Timestamp"],
                }
            )
    return flows


async def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, mode="r") as file:
        return json.load(file)


class Colors(Enum):
    SUCCESS = "\033[32m"  # Green text
    WARNING = "\033[33m"  # Yellow text
    ERROR = "\033[31m"  # Red text
    RESET = "\033[0m"  # Reset to default


def printTextColor(color: Colors, text: str):
    print(f"{color.value}[{color.name}] {text}{Colors.RESET.value}")

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

DATA_FILE = Path("expenses_data.json")


def load_data(file_path: Path) -> Dict:
    # if file not exist yet, make empty one
    if not file_path.exists():
        return {"budget": 500.0, "items": []}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(file_path: Path, data: Dict) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_expense(data: Dict, amount: float, category: str, note: str) -> None:
    if amount <= 0:
        print("amount must be bigger than 0")
        return
    item = {

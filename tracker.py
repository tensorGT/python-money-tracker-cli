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
        "amount": round(amount, 2),
        "category": category.strip().lower(),
        "note": note.strip(),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    data["items"].append(item)
    print("saved! spent %.2f on %s" % (item["amount"], item["category"]))


def set_budget(data: Dict, new_budget: float) -> None:
    if new_budget < 0:
        print("budget cannot be minus")
        return
    data["budget"] = round(new_budget, 2)
    print("ok budget is now %.2f" % data["budget"])


def get_category_totals(items: List[Dict]) -> Dict[str, float]:
    totals: Dict[str, float] = {}
    for it in items:
        cat = it["category"]
        totals[cat] = totals.get(cat, 0.0) + float(it["amount"])
    return totals


def show_summary(data: Dict, month_filter: Optional[str] = None) -> None:
    items = data["items"]
    if month_filter:
        items = [x for x in items if x["time"].startswith(month_filter)]

    totals = get_category_totals(items)
    spent = sum(totals.values())
    left = data["budget"] - spent

    print("=== My Spend Summary ===")
    if month_filter:
        print("Month:", month_filter)
    print("Total Budget : %.2f" % data["budget"])
    print("Total Spent  : %.2f" % spent)
    print("Money Left   : %.2f" % left)
    print("\nBy Category:")
    if not totals:
        print("  nothing here yet")
    for cat, val in sorted(totals.items()):
        print("  - %-12s : %.2f" % (cat, val))


def export_csv(data: Dict, out_path: Path, month_filter: Optional[str] = None) -> None:
    items = data["items"]
    if month_filter:
        items = [x for x in items if x["time"].startswith(month_filter)]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "category", "amount", "note"])
        for it in items:
            writer.writerow([it["time"], it["category"], it["amount"], it["note"]])
    print("exported %d rows to %s" % (len(items), out_path))


def export_monthly_report(data: Dict, month: str, out_path: Path) -> None:
    items = [x for x in data["items"] if x["time"].startswith(month)]
    totals = get_category_totals(items)
    spent = sum(totals.values())
    report = {
        "month": month,
        "budget": data["budget"],
        "total_spent": round(spent, 2),
        "remaining": round(data["budget"] - spent, 2),
        "categories": {k: round(v, 2) for k, v in totals.items()},
        "count": len(items),
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("monthly summary saved to", out_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="simple money tracker in terminal")
    parser.add_argument("--file", default=str(DATA_FILE), help="json file for save data")
    sub = parser.add_subparsers(dest="cmd")

    p_add = sub.add_parser("add", help="add new spend")
    p_add.add_argument("amount", type=float)
    p_add.add_argument("category", type=str)


#!/usr/bin/env python3
import json
from decimal import Decimal

latest = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line, parse_float=Decimal, parse_int=Decimal)
        except (json.JSONDecodeError, ValueError):
            continue

        if not isinstance(event, dict):
            continue

        txn_id = event.get("txn_id")
        ts = event.get("ts")

        if not txn_id or ts is None or "status" not in event:
            continue

        previous = latest.get(txn_id)

        if previous is None or ts >= previous["ts"]:
            latest[txn_id] = event

count = 0
total = Decimal("0")

for event in latest.values():
    if event["status"] == "success":
        count += 1
        try:
            total += Decimal(str(event["amount"]).replace(",", ""))
        except (KeyError, ValueError):
            raise ValueError("A successful transaction has an invalid amount")

with open("expected.txt", encoding="utf-8") as f:
    expected = int(f.read().strip())

if count != expected:
    raise SystemExit(
        f"Reconciliation failed: expected {expected}, found {count}"
    )

print(f"KOYA-{int(total)}")

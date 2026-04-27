#!/usr/bin/env python3
"""DeadOPT optimizer entrypoint."""

import json
import os
import sys

from improved_optimizer import optimize_code
from symbol_table import generate_symbol_table


def _lines_removed(before: str, after: str) -> int:
    return max(0, len(before.splitlines()) - len(after.splitlines()))


def main() -> None:
    if len(sys.argv) < 3:
        print(
            json.dumps(
                {
                    "error": "Usage: python main_optimizer.py <language> <file_path>",
                    "optimizedCode": "",
                    "linesRemoved": 0,
                    "report": {},
                    "symbolTable": [],
                }
            )
        )
        sys.exit(1)

    language = sys.argv[1].lower()
    file_path = sys.argv[2]

    if not os.path.exists(file_path):
        print(json.dumps({"error": f"File not found: {file_path}"}))
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as file:
        original_code = file.read()

    try:
        optimized = optimize_code(language, original_code)
        optimized_code = optimized["optimizedCode"]
        report = optimized["report"]

        symbol_table = generate_symbol_table(language, optimized_code)

        payload = {
            "optimizedCode": optimized_code,
            "linesRemoved": _lines_removed(original_code, optimized_code),
            "report": report,
            "symbolTable": symbol_table,
        }
        print(json.dumps(payload))
    except Exception as exc:
        print(
            json.dumps(
                {
                    "error": f"Optimization failed: {str(exc)}",
                    "optimizedCode": original_code,
                    "linesRemoved": 0,
                    "report": {"error": str(exc)},
                    "symbolTable": [],
                }
            )
        )
        sys.exit(1)

if __name__ == '__main__':
    main()
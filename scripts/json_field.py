#!/usr/bin/env python3
import json
import sys


def resolve_expr(data, expr: str):
    cur = data
    for part in expr.split("."):
        if part.isdigit():
            cur = cur[int(part)]
        else:
            cur = cur[part]
    return cur


def main():
    if len(sys.argv) != 3:
        print("Usage: json_field.py <json_file_or_-> <field.path>", file=sys.stderr)
        sys.exit(1)

    source = sys.argv[1]
    expr = sys.argv[2]

    if source == "-":
        data = json.load(sys.stdin)
    else:
        with open(source, "r", encoding="utf-8") as f:
            data = json.load(f)

    value = resolve_expr(data, expr)

    if isinstance(value, bool):
        print("true" if value else "false")
    else:
        print(value)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3

import json
import sys
from pathlib import Path

import yaml

from validate_users import validate


def generate(data):
    peers = []

    for user in data["users"]:
        peers.append({
            "name": user["name"],
            "group": user["group"],
            "address": f'{user["ip"]}/32',
            "allowed_ips": f'{user["ip"]}/32',
        })

    return {
        "interface": data["gateway"]["interface"],
        "peers": peers,
    }


def main():
    if len(sys.argv) != 2:
        sys.exit(
            "Usage: python scripts/generate_peers.py users.example.yaml"
        )

    path = Path(sys.argv[1])

    try:
        with path.open(encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except (OSError, yaml.YAMLError) as exc:
        sys.exit(f"ERROR: {exc}")

    errors = validate(data)

    if errors:
        print("GENERATION ABORTED")
        for error in errors:
            print(f" - {error}")
        sys.exit(1)

    result = generate(data)

    print(json.dumps(result, indent=2))
    print("\nDRY-RUN: no changes applied to WireGuard")


if __name__ == "__main__":
    main()
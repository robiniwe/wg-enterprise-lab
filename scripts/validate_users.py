#!/usr/bin/env python3

import ipaddress
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: Install PyYAML: python -m pip install PyYAML")


def validate(data):
    errors = []

    if not isinstance(data, dict):
        return ["YAML root must be a mapping"]

    groups = data.get("groups", {})
    users = data.get("users", [])

    if not isinstance(groups, dict) or not groups:
        errors.append("groups must be a non-empty mapping")
        groups = {}

    if not isinstance(users, list):
        errors.append("users must be a list")
        users = []

    networks = {}

    for name, group in groups.items():
        try:
            networks[name] = ipaddress.ip_network(
                group["subnet"], strict=True
            )
        except (KeyError, TypeError, ValueError):
            errors.append(f"Invalid subnet for group {name}")

    names = set()
    addresses = set()

    for index, user in enumerate(users, 1):
        if not isinstance(user, dict):
            errors.append(f"User #{index} must be a mapping")
            continue

        name = user.get("name")
        group = user.get("group")
        address = user.get("ip")

        if not isinstance(name, str) or not name.strip():
            errors.append(f"User #{index}: invalid name")
            continue

        if name in names:
            errors.append(f"Duplicate username: {name}")
        names.add(name)

        if group not in networks:
            errors.append(f"{name}: unknown group {group}")
            continue

        try:
            ip = ipaddress.ip_address(address)

            if ip.version != 4:
                errors.append(f"{name}: only IPv4 is supported")
                continue

            if ip not in networks[group]:
                errors.append(
                    f"{name}: {ip} outside {networks[group]}"
                )

            if ip in (
                networks[group].network_address,
                networks[group].broadcast_address
            ):
                errors.append(
                    f"{name}: reserved subnet address {ip}"
                )

            if ip in addresses:
                errors.append(f"Duplicate IP address: {ip}")

            addresses.add(ip)

        except ValueError:
            errors.append(f"{name}: invalid IP address")

    return errors


def main():
    if len(sys.argv) != 2:
        sys.exit(
            "Usage: python validate_users.py users.example.yaml"
        )

    path = Path(sys.argv[1])

    try:
        with path.open(encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except (OSError, yaml.YAMLError) as exc:
        sys.exit(f"ERROR: {exc}")

    errors = validate(data)

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f" - {error}")
        sys.exit(1)

    print("VALIDATION PASSED")
    print(json.dumps({
        "groups": len(data["groups"]),
        "users": len(data.get("users", []))
    }, indent=2))


if __name__ == "__main__":
    main()

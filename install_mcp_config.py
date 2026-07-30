#!/usr/bin/env python3
"""Merge a single MCP server entry into a client config file without touching
unrelated settings.

Usage:
    python install_mcp_config.py --client kimi --server-json '{"freecad": {...}}'
    python install_mcp_config.py --client claude --server-config-file /path/to/freecad.json
"""
import argparse
import json
import os
import sys


CLIENT_CONFIGS = {
    "kimi": os.path.join(os.path.expanduser("~"), ".kimi", "mcp.json"),
    "claude": os.path.join(os.path.expanduser("~"), ".claude", "settings.json"),
}


def merge_config(path: str, server_fragment: dict) -> dict:
    """Load existing config, create mcpServers if missing, and merge the
    provided server fragment. Only the keys inside the fragment are overwritten.
    """
    config: dict = {}
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as exc:
            print(f"ERROR: {path} contains invalid JSON: {exc}", file=sys.stderr)
            sys.exit(1)

    if not isinstance(config, dict):
        config = {}

    if "mcpServers" not in config:
        config["mcpServers"] = {}

    if not isinstance(config["mcpServers"], dict):
        config["mcpServers"] = {}

    for server_name, server_config in server_fragment.items():
        config["mcpServers"][server_name] = server_config

    return config


def main():
    parser = argparse.ArgumentParser(description="Register an MCP server in a client config.")
    parser.add_argument("--client", required=True, choices=list(CLIENT_CONFIGS),
                        help="Target client config (kimi or claude).")
    parser.add_argument("--server-json", help='JSON fragment containing one or more mcpServers entries, e.g. {"freecad": {...}}')
    parser.add_argument("--server-config-file", help="Path to a JSON file containing the server fragment (avoids shell quoting issues).")
    args = parser.parse_args()

    if not bool(args.server_json) ^ bool(args.server_config_file):
        parser.error("Specify exactly one of --server-json or --server-config-file.")

    try:
        if args.server_config_file:
            with open(args.server_config_file, "r", encoding="utf-8") as f:
                server_fragment = json.load(f)
        else:
            server_fragment = json.loads(args.server_json)
    except json.JSONDecodeError as exc:
        print(f"ERROR: server config is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(server_fragment, dict):
        print("ERROR: --server-json must be a JSON object.", file=sys.stderr)
        sys.exit(1)

    config_path = CLIENT_CONFIGS[args.client]
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    config = merge_config(config_path, server_fragment)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    print(f"Updated {config_path}")
    for name in server_fragment:
        print(f"  - registered '{name}'")


if __name__ == "__main__":
    main()

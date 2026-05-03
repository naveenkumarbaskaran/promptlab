"""CLI for promptlab."""

from __future__ import annotations

import argparse
import sys


from promptlab.store import PromptStore
from promptlab.diff import diff_prompts


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(prog="promptlab", description="Git for your prompts")
    parser.add_argument("--store", default=".prompts", help="Prompt store directory")
    subparsers = parser.add_subparsers(dest="command")

    # Init
    subparsers.add_parser("init", help="Initialize prompt store")

    # List
    subparsers.add_parser("list", help="List all prompts")

    # Show
    show_parser = subparsers.add_parser("show", help="Show a prompt")
    show_parser.add_argument("name", help="Prompt name")
    show_parser.add_argument("--version", type=int, default=None, help="Version number")

    # Diff
    diff_parser = subparsers.add_parser("diff", help="Diff two versions")
    diff_parser.add_argument("name", help="Prompt name")
    diff_parser.add_argument("v1", help="First version (e.g., v1 or 1)")
    diff_parser.add_argument("v2", help="Second version (e.g., v2 or 2)")

    # History
    history_parser = subparsers.add_parser("history", help="Show version history")
    history_parser.add_argument("name", help="Prompt name")

    # Validate
    subparsers.add_parser("validate", help="Validate all prompts")

    # Promote
    promote_parser = subparsers.add_parser("promote", help="Promote version to env")
    promote_parser.add_argument("name", help="Prompt name")
    promote_parser.add_argument("version", help="Version (e.g., v3 or 3)")
    promote_parser.add_argument("env", help="Environment (e.g., production)")

    args = parser.parse_args()
    store = PromptStore(args.store)

    if args.command == "init":
        store.init()
        print(f"Initialized prompt store at {args.store}/")

    elif args.command == "list":
        prompts = store.list_prompts()
        if not prompts:
            print("No prompts found. Run 'promptlab init' first.")
            return
        print(f"{'Name':<25} {'Version':>8} {'Versions':>8}")
        print("─" * 45)
        for p in prompts:
            print(f"{p['name']:<25} v{p['latest_version']:>6} {p['version_count']:>8}")

    elif args.command == "show":
        try:
            prompt = store.load(args.name, version=args.version)
            print(f"# {prompt.name} v{prompt.version}")
            print(f"# Hash: {prompt.hash}")
            print(f"# Variables: {prompt.variable_names}")
            print("─" * 40)
            print(prompt.template)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "diff":
        v1 = _parse_version(args.v1)
        v2 = _parse_version(args.v2)
        try:
            result = diff_prompts(store, args.name, v1, v2)
            if result:
                print(result)
            else:
                print("No differences found.")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "history":
        hist = store.history(args.name)
        if not hist:
            print(f"No history found for '{args.name}'")
            return
        for entry in hist:
            v = entry["version"]
            h = entry.get("hash", "?")
            print(f"  v{v}  {h}  {entry.get('metadata', {}).get('note', '')}")

    elif args.command == "validate":
        prompts = store.list_prompts()
        issues_found = False
        for p in prompts:
            prompt = store.load(p["name"])
            issues = prompt.validate()
            if issues:
                issues_found = True
                print(f"✗ {p['name']} v{p['latest_version']}:")
                for issue in issues:
                    print(f"    {issue}")
            else:
                print(f"✓ {p['name']} v{p['latest_version']}")
        if issues_found:
            sys.exit(1)

    elif args.command == "promote":
        v = _parse_version(args.version)
        store.promote(args.name, v, args.env)
        print(f"Promoted {args.name} v{v} → {args.env}")

    else:
        parser.print_help()


def _parse_version(text: str) -> int:
    """Parse 'v3' or '3' to int."""
    text = text.strip().lower()
    if text.startswith("v"):
        text = text[1:]
    return int(text)


if __name__ == "__main__":
    main()

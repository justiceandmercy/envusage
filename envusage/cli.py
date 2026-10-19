import argparse
import json
import sys
from pathlib import Path

from .scanner import scan_dir


def main():
    ap = argparse.ArgumentParser(
        prog="envusage",
        description="Compare env vars used in code with a declared template.",
    )
    ap.add_argument("path", nargs="?", default=".", help="project root")
    ap.add_argument("-t", "--template", help="path to .env template")
    ap.add_argument("--json", action="store_true", help="output JSON")
    args = ap.parse_args()
    root = Path(args.path).resolve()
    tmpl = Path(args.template).resolve() if args.template else None
    res = scan_dir(root, tmpl)
    if res.declared:
        undeclared = sorted(res.used - res.declared)
        unused = sorted(res.declared - res.used)
    else:
        undeclared = sorted(res.used)
        unused = []
    if args.json:
        print(json.dumps({
            "used": sorted(res.used),
            "declared": sorted(res.declared),
            "undeclared": undeclared,
            "unused": unused,
            "files_scanned": res.files_scanned,
        }, indent=2))
        return
    print(f"Scanned {res.files_scanned} files. Found {len(res.used)} env var references.")
    if res.declared:
        print(f"Declared in template: {len(res.declared)}")
    if undeclared:
        print("\nUndeclared (used in code but not in template):")
        for v in undeclared:
            print(f"  - {v}")
    if unused:
        print("\nUnused (declared but not referenced in code):")
        for v in unused:
            print(f"  - {v}")
    if res.declared and not undeclared and not unused:
        print("\nAll env vars match.")
    if not res.declared:
        print("\nNo template found; run with -t .env.example to compare.")


if __name__ == "__main__":
    main()

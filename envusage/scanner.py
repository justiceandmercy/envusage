"""Scan source files for environment variable references."""
import re
from dataclasses import dataclass, field
from pathlib import Path

PATTERNS = [
    re.compile(r"process\.env\.([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"process\.env\[['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\]"),
    re.compile(r"os\.environ\[['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\]"),
    re.compile(r"os\.environ\.get\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
    re.compile(r"os\.getenv\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
    re.compile(r"getenv\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
    re.compile(r"env\(['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\)"),
]

SOURCE_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rb", ".rs", ".java", ".sh"}
SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", ".tox"}


@dataclass
class ScanResult:
    used: set = field(default_factory=set)
    declared: set = field(default_factory=set)
    files_scanned: int = 0


def parse_declared(path: Path) -> set:
    names = set()
    if not path.exists():
        return names
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key = line.split("=", 1)[0].strip()
            if key.startswith("export "):
                key = key[len("export "):].strip()
            if key and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
                names.add(key)
    return names


def scan_text(text: str) -> set:
    found = set()
    for pat in PATTERNS:
        for m in pat.finditer(text):
            found.add(m.group(1))
    return found


def scan_dir(root: Path, template: Path = None) -> ScanResult:
    res = ScanResult()
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix not in SOURCE_EXTS:
            continue
        parts = p.relative_to(root).parts
        if any(part in SKIP_DIRS or part.startswith(".") for part in parts[:-1]):
            continue
        try:
            text = p.read_text(errors="ignore")
        except Exception:
            continue
        res.used |= scan_text(text)
        res.files_scanned += 1
    if template is None:
        for cand in (".env.example", ".env.sample", ".env.template"):
            candp = root / cand
            if candp.exists():
                template = candp
                break
    if template is not None:
        res.declared = parse_declared(template)
    return res

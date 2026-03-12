"""
Audit Dream Caesar for storage paths that still drift outside the repo-local root.

This scans text files for:
1) Windows absolute paths not rooted at D:\\dream-caesar
2) WSL / UNC local machine paths
3) external cloud/workspace URLs that indicate non-local storage/runtime dependencies

It writes a JSON report under recovery/ and prints a short summary.
"""

from __future__ import annotations

import json
import re
from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "recovery" / "local_storage_audit.json"
DEFAULT_SCAN_ROOTS = [
    PROJECT_ROOT / "src",
    PROJECT_ROOT / "scripts",
    PROJECT_ROOT / "config",
    PROJECT_ROOT / "CRONUS",
]

TEXT_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".jsonl", ".md", ".txt", ".toml",
    ".yaml", ".yml", ".sql", ".sh", ".bat", ".ps1", ".html", ".css", ".csv"
}
SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "exports",
    "recovery",
    "artifacts",
    "ajna",
    ".next",
}
MAX_FILE_BYTES = 1_000_000

WINDOWS_ABS_RE = re.compile(r"[A-Z]:\\(?![nrt\"'\\])[^\s\"']+")
UNC_RE = re.compile(r"\\\\(?![nrt\"'\\])[^\\\s]+\\[^\\\r\n\"']+")
WSL_RE = re.compile(r"/(?:home|mnt)/[^\s\"']+")
URL_RE = re.compile(r"https?://[^\s\"')]+")

ALLOWED_WINDOWS_ROOT = str(PROJECT_ROOT).lower().replace("/", "\\")
EXTERNAL_URL_HINTS = (
    "firebase", "airtable", "googleusercontent", "cloudworkstations", "studio.firebase",
    "notion.so", "openclaw.ai"
)


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def iter_text_files(scan_root: Path):
    for current_root, dir_names, file_names in scan_root.walk():
        dir_names[:] = [name for name in dir_names if name not in SKIP_DIR_NAMES]
        for file_name in file_names:
            path = current_root / file_name
            if not is_text_file(path):
                continue
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            yield path


def classify_match(match: str) -> str | None:
    lowered = match.lower()
    if any(token in match for token in ("[", "]", "(", ")", "{", "}", "|")):
        return None
    if re.match(r"^[a-z]:\\", lowered):
        normalized = lowered.replace("/", "\\")
        if normalized.startswith(r"c:\program"):
            return None
        if normalized.startswith(ALLOWED_WINDOWS_ROOT):
            return None
        return "external_windows_path"
    if match.startswith("\\\\"):
        return "unc_or_network_path"
    if match.startswith("/home/") or match.startswith("/mnt/"):
        return "wsl_or_linux_path"
    if match.startswith("http://") or match.startswith("https://"):
        if any(hint in lowered for hint in EXTERNAL_URL_HINTS):
            return "external_cloud_url"
    return None


def main() -> int:
    parser = ArgumentParser(description="Audit Dream Caesar source for non-local storage/runtime path references.")
    parser.add_argument(
        "--scan-root",
        action="append",
        default=[],
        help="Optional additional scan root(s). Defaults to src, scripts, config, and CRONUS under the repo root.",
    )
    args = parser.parse_args()

    findings: dict[str, list[dict[str, object]]] = defaultdict(list)
    file_count = 0
    scan_roots = [Path(root).resolve() for root in args.scan_root] if args.scan_root else DEFAULT_SCAN_ROOTS

    for scan_root in scan_roots:
        if not scan_root.exists():
            continue
        for path in iter_text_files(scan_root):
            file_count += 1
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            lines = text.splitlines()
            for line_no, line in enumerate(lines, start=1):
                matches = []
                matches.extend(WINDOWS_ABS_RE.findall(line))
                matches.extend(UNC_RE.findall(line))
                matches.extend(WSL_RE.findall(line))
                matches.extend(URL_RE.findall(line))
                for match in matches:
                    kind = classify_match(match)
                    if not kind:
                        continue
                    findings[kind].append(
                        {
                            "path": str(path),
                            "line": line_no,
                            "match": match,
                        }
                    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "scanned_text_files": file_count,
        "summary": {kind: len(items) for kind, items in sorted(findings.items())},
        "findings": findings,
    }
    REPORT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"REPORT={REPORT_PATH}")
    print(f"SCANNED_TEXT_FILES={file_count}")
    for kind, items in sorted(findings.items()):
        print(f"{kind}={len(items)}")
    if not findings:
        print("STATUS=clean")
    else:
        print("STATUS=findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

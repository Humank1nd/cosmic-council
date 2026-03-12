import argparse
import re
from datetime import datetime

from desktop_runtime import HANDOFF_DIR, ensure_runtime_dirs


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Dream Caesar handoff note and print the absolute path.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--from-seat", required=True)
    parser.add_argument("--to-seat", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--paths", nargs="+", required=True)
    parser.add_argument("--next", required=True)
    parser.add_argument("--watchout", default="Verify the listed paths before trusting them as canon.")
    args = parser.parse_args()

    ensure_runtime_dirs()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{slugify(args.task_id)}-{slugify(args.from_seat)}-to-{slugify(args.to_seat)}.md"
    output_path = HANDOFF_DIR / filename

    path_lines = "\n".join(f"- {path}" for path in args.paths)
    content = (
        f"# Handoff {args.task_id}\n\n"
        f"FROM: {args.from_seat.upper()}\n"
        f"TO: {args.to_seat.upper()}\n\n"
        f"## Summary\n\n"
        f"{args.summary}\n\n"
        f"## Paths\n\n"
        f"{path_lines}\n\n"
        f"## Watchout\n\n"
        f"{args.watchout}\n\n"
        f"## Next\n\n"
        f"{args.next}\n"
    )
    output_path.write_text(content, encoding="utf-8")
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

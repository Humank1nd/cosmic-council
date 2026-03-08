import os
import sys
from pathlib import Path


def _prepend_import_paths() -> Path:
    project_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "src"))
    sys.path.insert(0, str(project_root / "config"))
    return project_root


def main() -> None:
    _prepend_import_paths()

    os.environ.setdefault("ALLOW_ANONYMOUS", "true")
    os.environ.setdefault("API_HOST", "127.0.0.1")
    os.environ.setdefault("API_PORT", "8012")
    os.environ.setdefault("API_RELOAD", "false")

    host = os.environ["API_HOST"]
    port = int(os.environ["API_PORT"])

    try:
        import uvicorn
        from src.cosmic_council.core.api import app

        print(f"Starting Cosmic Council API on {host}:{port}")
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as exc:
        print(f"Error starting server: {exc}")
        import traceback

        traceback.print_exc()
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()

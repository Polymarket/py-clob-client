import os
import sys
from pathlib import Path

REQUIRED = ["HOST", "CHAIN_ID", "PRIVATE_KEY", "FUNDER"]

def load_dotenv(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

def main() -> int:
    dotenv = Path(".env")
    if dotenv.exists():
        load_dotenv(dotenv)

    missing = [k for k in REQUIRED if not os.environ.get(k)]
    if missing:
        print("Missing required env vars:")
        for k in missing:
            print(f"- {k}")
        return 1

    print("Env looks good.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

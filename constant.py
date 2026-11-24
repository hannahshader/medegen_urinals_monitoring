import os
from pathlib import Path


def _load_env(path):
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


_load_env(Path(__file__).resolve().parent / ".env")

CONNECT_TIMEOUT = 2
DB_CONFIG = {
    'host': os.getenv('HOST'),
    'database': os.getenv('DATABASE'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('PASSWORD'),
    'connect_timeout': int(CONNECT_TIMEOUT),
}
from collections import defaultdict
from pathlib import Path

import xxhash

files = defaultdict(list)


def hash_file_xxhash(file_path):
    h = xxhash.xxh128()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_for_files():
    start_path = Path.home()

    for i in start_path.rglob("*"):
        try:
            if i.is_file() and i.stat().st_size > 0:
                file_hash = hash_file_xxhash(i)
                files[file_hash].append(str(i))

        except PermissionError:
            continue
        except OSError:
            continue


def main():
    scan_for_files()


if __name__ == "__main__":
    main()

from collections import Counter
from pathlib import Path

import xxhash

files = Counter()


def hash_file_xxhash(file_path):
    h = xxhash.xxh128()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    files[str(h.hexdigest())] += 1


def scan_for_files():
    pathlist = Path("/")
    for p in pathlist.glob("*"):
        for i in p.rglob("*"):
            try:
                if i.is_file():
                    hash_file_xxhash(i)
            except PermissionError:
                print("perm den")
                continue
            except OSError:
                print("sys error")
                continue


def main():
    scan_for_files()
    print(files.most_common(5))


if __name__ == "__main__":
    main()

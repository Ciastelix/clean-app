import xxhash


def hash_file_xxhash(file_path):
    h = xxhash.xxh128()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    print(hash_file_xxhash("./uv.lock"))


if __name__ == "__main__":
    main()

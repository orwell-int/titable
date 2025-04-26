import platform
import time
import os


def is_micropython():
    return platform.platform().startswith("MicroPython")


if is_micropython():

    def get_timeref_ms():
        return time.ticks_ms()

    def dir_exists(filename: str):
        try:
            return (os.stat(filename)[0] & 0x4000) != 0
        except OSError:
            return False

    def file_exists_and_not_empty(filename: str):
        try:
            stat = os.stat(filename)
            return ((stat[0] & 0x4000) == 0) and (stat[6] > 0)
        except OSError:
            return False

    def is_file(filename: str):
        try:
            stat = os.stat(filename)
            return (stat[0] & 0x8000) == 1
        except OSError:
            return False

else:

    def get_timeref_ms():
        return time.monotonic() * 1000

    def dir_exists(filename: str):
        return os.path.exists(filename)

    def file_exists_and_not_empty(filename: str):
        return os.path.exists(filename) and os.path.getsize(filename) > 0

    def is_file(filename: str):
        return os.path.isfile(filename)


def create_dir(path: str):
    create_dirs(path.split("/"))


def create_dirs(paths: list[str]):
    print(f"create_dirs({paths})")
    full_path = ""
    has_empty = False
    first_non_empty = True
    for path in paths:
        if path:
            if first_non_empty:
                if has_empty:
                    full_path = "/"
                first_non_empty = False
            else:
                if full_path:
                    full_path += "/"
            full_path += path
            if not dir_exists(full_path):
                os.mkdir(full_path)
        else:
            has_empty = True


def create_file(filename: str, content: str):
    parts = filename.split("/")
    create_dirs(parts[:-1])
    open(filename, "w").write(content)


def remove_in(folder):
    for file in os.listdir(folder):
        full_filename = f"{folder}/{file}"
        if 0x4000 == os.stat(full_filename):
            remove_in(full_filename)
        else:
            os.remove(full_filename)


def main():
    print(f"Is MicroPython ? {is_micropython()}")


if "__main__" == __name__:
    main()

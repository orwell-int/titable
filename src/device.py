import platform
import time
import os


def is_micropython():
    return platform.platform().startswith("MicroPython")


if is_micropython():

    def get_timeref_ms():
        return time.ticks_ms()

    import requests2

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

else:

    def get_timeref_ms():
        return time.monotonic() * 1000

    import requests as requests2

    def dir_exists(filename: str):
        return os.path.exists(filename)

    def file_exists_and_not_empty(filename: str):
        return os.path.exists(filename) and os.path.getsize(filename) > 0


def create_dirs(paths: list[str]):
    full_path = ""
    for path in paths:
        if full_path:
            full_path += "/"
        full_path += path
        if not dir_exists(full_path):
            os.mkdir(full_path)


def create_file(filename: str, content: str):
    parts = filename.split("/")
    device.create_dirs(parts[:-1])
    open(filename, "w").write(content)


def main():
    print(f"Is MicroPython ? {is_micropython()}")


if "__main__" == __name__:
    main()

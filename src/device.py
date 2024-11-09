import platform
import time


def is_micropython():
    return platform.platform().startswith("MicroPython")


if is_micropython():

    def get_timeref_ms():
        return time.ticks_ms()

else:

    def get_timeref_ms():
        return time.monotonic() * 1000


def main():
    print(f"Is MicroPython ? {is_micropython()}")


if "__main__" == __name__:
    main()

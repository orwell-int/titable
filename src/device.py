import platform


def is_micropython():
    return platform.platform().startswith("MicroPython")


def main():
    print(f"Is MicroPython ? {is_micropython()}")


if "__main__" == __name__:
    main()

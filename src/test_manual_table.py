import os

import file_mock
import table
import device


def main():
    import os

    print("cwd:", os.getcwd())
    print("os.listdir()", os.listdir("."))
    with file_mock.do():
        print("-- Mock --")
        print("cwd:", os.getcwd())
        print("os.listdir()", os.listdir("."))
        print("device.create_dir('toto')", device.create_dir("toto"))
        table.main()


if "__main__" == __name__:
    main()

import sys
from contextlib import contextmanager
from pathlib import PurePosixPath

import unittest.mock
from unittest.mock import Mock

CONTENT = {}
STATS = {}
PRINT_IN_MOCK = True
# set this to True to dump the content of the mock (to potentially reuse it)
PRINT_DATA = False


class MockOpen(Mock):
    def __init__(self, path, mode):
        path = str(PurePosixPath(path))
        global PRINT_IN_MOCK
        if PRINT_IN_MOCK:
            print(f"MockOpen.__init__(path={path}, mode={mode})")
        self.path = path
        self.mode = mode

    def __getattr__(self, name):
        """
        This ignores a lot of what can be called.
        The idea is not to build the perfect mock,
        but enough to go through some tests without
        writing to the disk.
        """
        # print(f"MockOpen.__getattr__(name={name})")
        if "write" == name:
            return self._write
        if "read" == name:
            return self._read

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def _write(self, content):
        global CONTENT
        CONTENT[self.path] = content
        global STATS
        STATS[self.path] = 0x8000
        global PRINT_IN_MOCK
        if PRINT_IN_MOCK:
            print(f"MockOpen.__write__(content={content})")

    def _read(self):
        global CONTENT
        global PRINT_IN_MOCK
        if PRINT_IN_MOCK:
            print(f"MockOpen.__read__() -> {CONTENT[self.path]}")
        return CONTENT[self.path]


def mock_dir_exists_results(path):
    global CONTENT
    path = str(PurePosixPath(path))
    global PRINT_IN_MOCK
    if PRINT_IN_MOCK:
        print(f"mock_dir_exists_results({path}) -> {path in CONTENT}")
    return path in CONTENT


def mock_create_dir_results(path):
    global PRINT_IN_MOCK
    if PRINT_IN_MOCK:
        print(f"mock_create_dir_results({path})")
    global CONTENT
    global STATS
    p = PurePosixPath(path)
    for parent in p.parents:
        CONTENT[str(parent)] = None
        STATS[str(parent)] = 0x4000
    CONTENT[str(p)] = None
    STATS[str(p)] = 0x4000


# it is a bit of a hack to rely on mock_create_dir_results
def mock_create_dirs_results(paths):
    global PRINT_IN_MOCK
    if PRINT_IN_MOCK:
        print(f"mock_create_dirs_results({paths})")
    if not paths:
        return
    path = "/" + "/".join(paths)
    mock_create_dir_results(path)


def mock_exists_results(path):
    global CONTENT
    path = str(PurePosixPath(path))
    return path in CONTENT


def mock_isfile_results(path):
    global STATS
    path = str(PurePosixPath(path))
    return (path in STATS) and (STATS[path] == 0x8000)


def mock_getsize_results(path):
    global CONTENT
    path = str(PurePosixPath(path))
    if path in CONTENT:
        return len(CONTENT[path])
    else:
        return -1


def mock_remove_results(path):
    global CONTENT
    path = str(PurePosixPath(path))
    if path in CONTENT:
        del CONTENT[path]
    global STATS
    if path in STATS:
        del STATS[path]


def mock_rename_results(old_path, new_path):
    global CONTENT
    old_path = str(PurePosixPath(old_path))
    new_path = str(PurePosixPath(new_path))
    if old_path in CONTENT:
        CONTENT[new_path] = CONTENT[old_path]
        del CONTENT[old_path]
    global STATS
    if old_path in STATS:
        STATS[new_path] = STATS[old_path]
        del STATS[old_path]


def mock_stat_results(path):
    global PRINT_IN_MOCK
    if PRINT_IN_MOCK:
        print(f"mock_stat_results({path})")
    global STATS
    return STATS[path]


def mock_listdir_results(path):
    global CONTENT
    path = str(PurePosixPath(path))
    result = []
    length = len(path) + 1
    for p in CONTENT:
        if p.startswith(path):
            if len(p) >= length:
                found = p.find("/", length)
                if -1 == found:
                    result.append(p[length:])
    global PRINT_IN_MOCK
    if PRINT_IN_MOCK:
        print(f"mock_listdir_results({path}) -> {result}")
    return result


def print_content():
    global CONTENT
    sys.stdout.write("CONTENT = {")
    last_index = len(CONTENT) - 1
    for i, (key, value) in enumerate(CONTENT.items()):
        if value is not None:
            len_value = len(value)
            if len_value > 40:
                value = value[:37] + b"..."
        sys.stdout.write(f'"{key}" : "{value}"')
        if i < last_index:
            sys.stdout.write(", ")
    sys.stdout.write("}\n")


class ClearContent:
    def __init__(self, print_data=False):
        self._print_data = print_data

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        global CONTENT
        global STATS
        if self._print_data:
            print("CONTENT")
            print(CONTENT)
            print("STATS")
            print(STATS)
        print("Clear content")
        CONTENT = {}
        STATS = {}


@contextmanager
def do():
    try:
        with (
            unittest.mock.patch("device.dir_exists") as mock_dir_exists,
            unittest.mock.patch("device.create_dir") as mock_create_dir,
            unittest.mock.patch("device.create_dirs") as mock_create_dirs,
            unittest.mock.patch("os.remove") as mock_remove,
            unittest.mock.patch("os.rename") as mock_rename,
            unittest.mock.patch("os.stat") as mock_stat,
            unittest.mock.patch("os.listdir") as mock_listdir,
            unittest.mock.patch("os.path.exists") as mock_exists,
            unittest.mock.patch("os.path.isfile") as mock_isfile,
            unittest.mock.patch("os.path.getsize") as mock_getsize,
            unittest.mock.patch("builtins.open", MockOpen),
            ClearContent(print_data=PRINT_DATA),
        ):
            mock_dir_exists.side_effect = mock_dir_exists_results
            mock_create_dir.side_effect = mock_create_dir_results
            mock_remove.side_effect = mock_remove_results
            mock_rename.side_effect = mock_rename_results
            mock_stat.side_effect = mock_stat_results
            mock_listdir.side_effect = mock_listdir_results
            mock_exists.side_effect = mock_exists_results
            mock_isfile.side_effect = mock_isfile_results
            mock_getsize.side_effect = mock_getsize_results
            yield
    finally:
        pass

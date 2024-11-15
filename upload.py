import subprocess
import os
import sys
import json
import hashlib

from pathlib import Path


def upload(port, source, destination):
    args = ["ampy", "--port", str(port), "put", source, destination]
    print(" ".join([str(a) for a in args]))
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("return code:", result.returncode)
        print("stdout:\n" + result.stdout.decode("utf8"))
        print("stderr:\n" + result.stderr.decode("utf8"))
        raise Exception(f"Failed to copy {source}")

def get_remote_hashes(port):
    args = ["ampy", "--port", str(port), "run", "hash.py"]
    print(" ".join([str(a) for a in args]))
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("return code:", result.returncode)
        print("stdout:\n" + result.stdout.decode("utf8"))
        print("stderr:\n" + result.stderr.decode("utf8"))
        raise Exception(f"Failed to run hash.py")
    return json.loads(result.stdout.decode("utf8"))


def get_local_hash(file):
    hash = hashlib.sha256(open(file, "rb").read())
    return hash.hexdigest()


def main():
    port = "COM9"
    sources = Path("src")
    hashes = get_remote_hashes(port)
    print(hashes)
    for file in sources.glob("*.py"):
        print(file)
        do_upload = True
        destination = (Path("/flash") / file.name).as_posix()
        if destination in hashes:
            remote_hash = hashes[destination]
            hash = get_local_hash(file)
            if hash == remote_hash:
                do_upload = False
                print("No need to upload")
        if do_upload:
            upload(port, file, destination)


if "__main__" == __name__:
    main()
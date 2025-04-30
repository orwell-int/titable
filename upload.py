import argparse
import subprocess
import os
import sys
import json
import hashlib
import serial.tools.list_ports

from pathlib import Path



def upload(port, baud, source, destination):
    args = [
        "ampy",
        "--port",
        str(port),
        "--baud",
        str(baud),
        "put",
        source,
        destination,
    ]
    print(" ".join([str(a) for a in args]))
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("return code:", result.returncode)
        print("stdout:\n" + result.stdout.decode("utf8"))
        print("stderr:\n" + result.stderr.decode("utf8"))
        raise Exception(f"Failed to copy {source}")


def get_remote_hashes(port, baud):
    args = ["ampy", "--port", str(port), "--baud", str(baud), "run", "hash.py"]
    print(" ".join([str(a) for a in args]))
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("return code:", result.returncode)
        print("stdout:\n" + result.stdout.decode("utf8"))
        print("stderr:\n" + result.stderr.decode("utf8"))
        raise Exception(f"Failed to run hash.py")
    return json.loads(result.stdout.decode("utf8"))


def reset_soft(port, baud):
    args = ["ampy", "--port", str(port), "--baud", str(baud), "run", "reset_soft.py"]
    print(" ".join([str(a) for a in args]))
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("return code:", result.returncode)
        print("stdout:\n" + result.stdout.decode("utf8"))
        print("stderr:\n" + result.stderr.decode("utf8"))
        raise Exception(f"Failed to run reset_soft.py")


def get_local_hash(file):
    hash_ = hashlib.sha256(open(file, "rb").read())
    return hash_.hexdigest()


def main():
    default_port = None
    ports = serial.tools.list_ports.comports()
    sorted_ports = sorted(ports)
    for port, desc, hwid in sorted_ports:
        print("{}: {} [{}]".format(port, desc, hwid))
        if default_port is None:
            if hwid.startswith("USB"):
                default_port = port
    if default_port is None:
        for port, desc, hwid in sorted_ports:
            print("{}: {} [{}]".format(port, desc, hwid))
            if default_port is None:
                default_port = port
    if default_port is None:
        default_port = "COM9"
    print("Default port", default_port)
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", default=None)
    parser.add_argument("--baud", "-b", default=115200)
    parser.add_argument("--dry-run", "-n", default=False, action="store_true")
    parser.add_argument("--reset", default=False, action="store_true")
    args = parser.parse_args()
    if args.port:
        port = args.port
    else:
        port = default_port
    sources = Path("src")
    hashes = get_remote_hashes(port, args.baud)
    print(hashes)
    for file in sources.glob("*.py"):
        if file in ("file_mock.py",) or file.name.startswith("test_"):
            continue
        print(file)
        do_upload = True
        destination = (Path("/flash") / file.name).as_posix()
        if destination in hashes:
            remote_hash = hashes[destination]
            hash_ = get_local_hash(file)
            if hash_ == remote_hash:
                do_upload = False
                print("No need to upload")
        if do_upload:
            if args.dry_run:
                print(f"Would have uploaded file {file} at {destination}")
            else:
                upload(port, args.baud, file, destination)
    if args.reset:
        if args.dry_run:
            print("Would have performed a soft reset")
        else:
            reset_soft(port, args.baud)


if "__main__" == __name__:
    main()

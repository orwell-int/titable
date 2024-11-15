import hashlib
import sys
import os
import json
import binascii


def main():
    digests = {}
    folder = "/flash"
    for file in os.listdir(folder):
        if not file.endswith(".py") or file in ("boot.py", "main.py",):
            continue
        
        path = folder + "/" + file
        hash = hashlib.sha256(open(file).read())
        digest = binascii.hexlify(hash.digest())
        digests[path] = digest
    print(json.dumps(digests))

if "__main__" == __name__:
    main()
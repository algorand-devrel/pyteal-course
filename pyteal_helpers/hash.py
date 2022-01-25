import base64
import hashlib
import sys

def sha256b64(s: str) -> str:
    return base64.b64encode(hashlib.sha256(str(s).encode("utf-8")).digest()).decode("utf-8")

if __name__ == "__main__":
    s = sys.argv[1]

    print(s)
    print(sha256b64(s))

import hashlib
import base64

s = "r-123647889123679"

print(s)
print(base64.b64encode(hashlib.sha256(str(s).encode("utf-8")).digest()).decode("utf-8"))

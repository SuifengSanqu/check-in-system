from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

from config import AES_KEY


def encrypt(text: str) -> str:
    cipher = AES.new(AES_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(text.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode()
    ct = base64.b64encode(ct_bytes).decode()
    return f"{iv}:{ct}"


def decrypt(encrypted: str) -> str:
    iv, ct = encrypted.split(":")
    iv = base64.b64decode(iv)
    ct = base64.b64decode(ct)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

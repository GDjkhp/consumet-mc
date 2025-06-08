import base64
from binascii import unhexlify
import os
from typing import Optional
from Crypto.Cipher import AES
from Crypto.Hash import MD5


def aes_unsalt(key: bytes, salt: bytes, key_len=32, iv_len=16):
    key_iv = b""
    prev = b""
    while len(key_iv) < (key_len + iv_len):
        prev = MD5.new(prev + key + salt).digest()
        key_iv += prev
    return key_iv[:key_len], key_iv[key_len : key_len + iv_len]


def aes_decrypt(ciphertext_b64: str, key: str, iv: Optional[str] = None):
    ciphertext = base64.b64decode(ciphertext_b64)
    key_encoded = key.encode()
    iv_encoded = iv.encode() if iv is not None else iv

    if ciphertext[:8] == b"Salted__":
        salt = ciphertext[8:16]
        ciphertext = ciphertext[16:]
        key_encoded, iv_encoded = aes_unsalt(key_encoded, salt)

    cipher = AES.new(key_encoded, AES.MODE_CBC, iv_encoded)
    decrypted = cipher.decrypt(ciphertext)

    # Remove PKCS#7 padding
    pad_len = decrypted[-1]
    return decrypted[:-pad_len].decode("latin-1")


def aes_encrypt(
    data: str, key: str, iv: Optional[str] = None, hexed: Optional[bool] = False
) -> bytes:
    b_size = 16
    data = data + (b_size - len(data) % b_size) * chr(b_size - len(data) % b_size)
    key_encoded = key.encode() if not hexed else unhexlify((key))
    if iv:
        iv_encoded = iv.encode() if not hexed else unhexlify(iv)
    else:
        iv_encoded = None

    cipher = AES.new(key_encoded, AES.MODE_CBC, iv_encoded)
    return base64.b64encode(cipher.encrypt(data.encode()))


def get_random_values(arr_view: memoryview):
    arr_view[:] = os.urandom(len(arr_view))
    return 0

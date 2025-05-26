from __future__ import annotations
import base64
from Crypto.Cipher import AES
from binascii import unhexlify

class AESCipher(object):

    def __init__(self, key: str, iv: str,hexed:bool = False ) -> None: 
        self._bs: int = AES.block_size
        self._key: bytes = key.encode() if not hexed else unhexlify(key)
        self._iv: bytes = iv.encode() if not hexed else unhexlify(iv)

    def encrypt(self, data: str) -> bytes:
        data = self._pad(data)
        cipher = AES.new(self._key, AES.MODE_CBC,self._iv)
        return base64.b64encode(cipher.encrypt(data.encode()))

    def decrypt(self, enc_data: bytes) -> str:
        enc_data = base64.b64decode(enc_data)
        cipher = AES.new(self._key, AES.MODE_CBC, self._iv)
        return AESCipher._unpad(cipher.decrypt(enc_data)).decode('utf-8')

    def _pad(self, s: str):
        return s + (self._bs - len(s) % self._bs) * chr(self._bs - len(s) % self._bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

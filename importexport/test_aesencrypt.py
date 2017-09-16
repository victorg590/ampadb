from unittest import TestCase
from . import aesencrypt
from io import BytesIO
from Crypto import Random
from random import randint, choice
import string

class EncryptTestCase(TestCase):
    def _get_content(self):
        prng = Random.new()
        content = prng.read(randint(1, 16) * 16)
        prng.close()
        return content

    def _gen_password(self):
        characters = randint(1, 100)
        return ''.join(choice(string.printable) for _ in range(characters))

    def test_encrypt_decrypt_same_content(self):
        content = self._get_content()
        password = self._gen_password()
        inp = BytesIO(content)
        enc = BytesIO()
        iv = aesencrypt.encrypt(inp, enc, password)
        enc.seek(0)
        out = BytesIO()
        aesencrypt.decrypt(enc, out, password, iv)
        self.assertEqual(out.getvalue(), content)
    
    def test_decrypt_failed_password(self):
        content = self._get_content()
        password1 = self._gen_password()
        password2 = self._gen_password()
        inp = BytesIO(content)
        enc = BytesIO()
        iv = aesencrypt.encrypt(inp, enc, password1)
        enc.seek(0)
        out = BytesIO()
        aesencrypt.decrypt(enc, out, password2, iv)
        self.assertNotEqual(out.getvalue(), content)
    
    def test_invalid_iv(self):
        content = self._get_content()
        password = self._gen_password()
        inp = BytesIO(content)
        enc = BytesIO()
        aesencrypt.encrypt(inp, enc, password)
        enc.seek(0)
        out = BytesIO()
        aesencrypt.decrypt(enc, out, password, b'\x00' * 16)
        self.assertNotEqual(out.getvalue(), content)

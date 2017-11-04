from unittest import TestCase
from io import BytesIO
from random import randint, choice
import string
from Crypto import Random
from . import aesencrypt


class EncryptTestCase(TestCase):
    @staticmethod
    def _get_content():
        prng = Random.new()
        content = prng.read(randint(1, 16) * 16)
        prng.close()
        return content

    @staticmethod
    def _gen_password():
        characters = randint(1, 100)
        return ''.join(choice(string.printable) for _ in range(characters))

    def test_same_content(self):
        content = self._get_content()
        password = self._gen_password()
        inp = BytesIO(content)
        enc = BytesIO()
        init_vector = aesencrypt.gen_init_vector()
        aesencrypt.encrypt(inp, enc,
                           aesencrypt.CryptoParams(password, init_vector))
        enc.seek(0)
        out = BytesIO()
        aesencrypt.decrypt(enc, out,
                           aesencrypt.CryptoParams(password, init_vector))
        self.assertEqual(out.getvalue(), content)

    def test_decrypt_failed_password(self):
        content = self._get_content()
        password1 = self._gen_password()
        password2 = self._gen_password()
        inp = BytesIO(content)
        enc = BytesIO()
        init_vector = aesencrypt.gen_init_vector()
        aesencrypt.encrypt(inp, enc,
                           aesencrypt.CryptoParams(password1, init_vector))
        enc.seek(0)
        out = BytesIO()
        aesencrypt.decrypt(enc, out,
                           aesencrypt.CryptoParams(password2, init_vector))
        self.assertNotEqual(out.getvalue(), content)

    def test_invalid_iv(self):
        content = self._get_content()
        password = self._gen_password()
        inp = BytesIO(content)
        enc = BytesIO()
        iv1 = aesencrypt.gen_init_vector()
        aesencrypt.encrypt(inp, enc, aesencrypt.CryptoParams(password, iv1))
        enc.seek(0)
        out = BytesIO()
        iv2 = aesencrypt.gen_init_vector()
        aesencrypt.decrypt(enc, out, aesencrypt.CryptoParams(password, iv2))
        self.assertNotEqual(out.getvalue(), content)

from typing import Tuple
from . import MathTools


class RSA:
    def __init__(self, key_size: int):
        self._key_size: int = key_size
        self._chunk_size: int = key_size // 8
        self._public_key: Tuple[int, int] | None = None
        self._private_key: Tuple[int, int] | None = None
        self._generate_keys(MathTools.prime_generator(self._key_size), MathTools.prime_generator(self._key_size))

    @property
    def public_key(self) -> Tuple[int, int]:
        return self._public_key

    @property
    def private_key(self) -> Tuple[int, int]:
        return self._private_key

    def _generate_keys(self, p: int, q: int):
        n: int = p * q
        phi: int = (p - 1) * (q - 1)
        # e: int = random.choice([i for i in range(1, phi) if gcd(i, phi) == 1])
        e = 65537
        d = MathTools.ext_euclidian_alg(e, phi)[0]
        if d < 0:
            d += phi

        self._public_key = (e, n)
        self._private_key = (d, n)

    def encrypt(self, text: str):
        cipher_blocks = []
        for i in range(0, len(text), self._chunk_size):
            block = text[i: i + self._chunk_size]
            bytesarray = bytearray(block.encode('UTF-8'))
            integer = int.from_bytes(bytesarray, byteorder='big', signed=False)
            r = MathTools.fast_exponentiation(integer, self._public_key[0], self._public_key[1])
            cipher_blocks.append(str(r))
        return " ".join(cipher_blocks)

    def decrypt(self, cipher: str):
        decrypted_blocks = []
        cipher_blocks = cipher.split(" ")
        for block in cipher_blocks:
            integer = int(block)
            integer = MathTools.fast_exponentiation(integer, self._private_key[0], self._private_key[1])
            bytesarray = integer.to_bytes(length=(8 + (integer + (integer < 0)).bit_length()) // 8, byteorder='big', signed=False)
            decrypted_blocks.append(bytesarray.decode('UTF-8'))
        return "".join(decrypted_blocks)

    @staticmethod
    def encrypt_with_key(text: str, key: Tuple[int, int], chunk_size: int):
        cipher_blocks = []
        for i in range(0, len(text), chunk_size):
            block = text[i: i + chunk_size]
            bytesarray = bytearray(block.encode('UTF-8'))
            integer = int.from_bytes(bytesarray, byteorder='big', signed=False)
            r = MathTools.fast_exponentiation(integer, key[0], key[1])
            cipher_blocks.append(str(r))
        return " ".join(cipher_blocks)

    @staticmethod
    def decrypt_with_key(cipher: str, key: Tuple[int, int], chunk_size: int):
        decrypted_blocks = []
        cipher_blocks = cipher.split(" ")
        for block in cipher_blocks:
            integer = int(block)
            integer = MathTools.fast_exponentiation(integer, key[0], key[1])
            bytesarray = integer.to_bytes(length=(8 + (integer + (integer < 0)).bit_length()) // 8, byteorder='big', signed=False)
            decrypted_blocks.append(bytesarray.decode('UTF-8'))
        return "".join(decrypted_blocks)

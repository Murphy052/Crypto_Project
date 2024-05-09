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
        bytesarray = bytearray(text.encode('UTF-8'))
        integer = int.from_bytes(bytesarray, byteorder='big', signed=False)
        r = MathTools.fast_exponentiation(integer, self._public_key[0], self._public_key[1])
        return r

    def decrypt(self, cipher: str):
        integer = int(cipher)
        integer = MathTools.fast_exponentiation(integer, self._private_key[0], self._private_key[1])
        bytesarray = integer.to_bytes(length=(8 + (integer + (integer < 0)).bit_length()) // 8, byteorder='big', signed=False)
        return bytesarray.decode('UTF-8')


def main() -> None:
    rsa: RSA = RSA(512)
    t = "Cryptography is Interesting!"
    r = rsa.encrypt(t)
    print(r)
    r = rsa.decrypt(str(r))
    print(r)


if __name__ == "__main__":
    main()

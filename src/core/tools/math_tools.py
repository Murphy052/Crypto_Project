import secrets
from typing import List


class MathTools:
    @staticmethod
    def ext_euclidian_alg(a: int, b: int):
        # make 'a' the bigger one and 'b' the lesser one
        swapped = False
        if a < b:
            a, b = b, a
            swapped = True

        # ca and cb store current a and b in form of
        # coefficients with initial a and b
        # a' = ca[0] * a + ca[1] * b
        # b' = cb[0] * a + cb[1] * b
        ca = (1, 0)
        cb = (0, 1)

        while b != 0:
            # k denotes how many times number b
            # can be substracted from a
            k = a // b
            # a  <- b
            # b  <- a - b * k
            # ca <- cb
            # cb <- (ca[0] - k * cb[0], ca[1] - k * cb[1])
            a, b, ca, cb = b, a - b * k, cb, (ca[0] - k * cb[0], ca[1] - k * cb[1])
        if swapped:
            return ca[1], ca[0]
        else:
            return ca

    @staticmethod
    def fast_exponentiation(num: int, p: int, div: int) -> int:
        size: int = 0
        tmp: int = 1

        while p >= tmp:
            tmp <<= 1
            size += 1
        size -= 1

        # calculate the result
        r = 1
        for i in range(size, -1, -1):
            r = (r * r) % div
            if (p >> i) & 1:
                r = (r * num) % div
        return r

    @staticmethod
    def prime_generator(size: int):
        while True:
            num = (1 << (size - 1)) + secrets.randbits(size - 1) - 10

            num -= num % 10
            num += 3  # 3 (mod 10)

            # heuristic test
            if MathTools.fast_exponentiation(2, num - 1, num) == 1 and MathTools.fib_mod(num + 1, num) == 0:
                return num

            num += 4
            if MathTools.fast_exponentiation(2, num - 1, num) == 1 and MathTools.fib_mod(num + 1, num) == 0:
                return num


    @staticmethod
    def matrix_mult(A: List[list[int]], B: List[list[int]], mod: int) -> List[list[int]]:
        """Multiplies two 2x2 matrices A and B under modulo."""
        return [[(A[0][0] * B[0][0] + A[0][1] * B[1][0]) % mod,
                 (A[0][0] * B[0][1] + A[0][1] * B[1][1]) % mod],
                [(A[1][0] * B[0][0] + A[1][1] * B[1][0]) % mod,
                 (A[1][0] * B[0][1] + A[1][1] * B[1][1]) % mod]]

    @staticmethod
    def matrix_pow(M: List[list[int]], power: int, mod: int):
        """Raises the matrix M to the power 'power' under modulo."""
        result = [[1, 0], [0, 1]]  # Identity matrix
        base = M

        while power:
            if power % 2 == 1:
                result = MathTools.matrix_mult(result, base, mod)
            base = MathTools.matrix_mult(base, base, mod)
            power //= 2

        return result

    @staticmethod
    def fib_mod(n, mod):
        """Returns the nth Fibonacci number modulo 'mod'."""
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            F = [[1, 1], [1, 0]]
            result = MathTools.matrix_pow(F, n - 1, mod)
            return result[0][0]


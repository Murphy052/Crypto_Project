async function rsa(method, msg = "") {
    let pyodide = await loadPyodide({
      indexURL: "https://cdn.jsdelivr.net/pyodide/v0.20.0/full/",
    });

    let code = `
import secrets
from typing import List, Tuple


class MathTools:
    @staticmethod
    def ext_euclidian_alg(a: int, b: int):
        swapped = False
        if a < b:
            a, b = b, a
            swapped = True

        ca = (1, 0)
        cb = (0, 1)

        while b != 0:
            k = a // b
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
        
class RSA:
    @staticmethod
    def generate_keys():
        p = MathTools.prime_generator(1024)
        q = MathTools.prime_generator(1024)
        n: int = p * q
        phi: int = (p - 1) * (q - 1)
        # e: int = random.choice([i for i in range(1, phi) if gcd(i, phi) == 1])
        e = 65537
        d = MathTools.ext_euclidian_alg(e, phi)[0]
        if d < 0:
            d += phi

        str_n = str(n)
        str_d = str(d)
        str_e = str(e)
        return '{"n": "' + str_n + '", "d": "' + str_d + '", "e": ' + str_e + '}'

    @staticmethod
    def encrypt_with_key(text: str, key: Tuple[int, int]):
        bytesarray = bytearray(text.encode('UTF-8'))
        integer = int.from_bytes(bytesarray, byteorder='big', signed=False)
        r = MathTools.fast_exponentiation(integer, key[0], key[1])
        return r

    @staticmethod
    def decrypt_with_key(cipher: str, key: Tuple[int, int]):
        integer = int(cipher)
        integer = MathTools.fast_exponentiation(integer, key[0], key[1])
        bytesarray = integer.to_bytes(length=(8 + (integer + (integer < 0)).bit_length()) // 8, byteorder='big', signed=False)
        return bytesarray.decode('UTF-8')

`;
    switch (method){
        case "encrypt":
        case "decrypt":
            const keys = JSON.parse(localStorage.getItem('serverPublicKeys'));
            code += `RSA.${method}_with_key(${msg}, (${keys.e}, int(${keys.n})))`
            break;
        case "generate_keys":
            code += `RSA.${method}()`
            break;
        default:
            console.log("Wrong method");
            return
    }
         

    let result = pyodide.runPython(code);
    console.log(result);
    return result
}

const generate_keys = async function() {
    if (localStorage.getItem("clientKeys") == null) {
        let result = await rsa("generate_keys");
        localStorage.setItem("clientKeys", result);
    }
}

const request = function(user) {
    fetch(`http://localhost:8000/kdc/public-key/${user}`, {
      method: 'GET',
    })
    .then(response => response.json()) // Parse response as JSON
    .then(data => {
        if (data) {
            console.log(rsa("decrypt", data));                        
            // localStorage.setItem(user, ) = `authorization=${data.token_type} ${data.access_token}`;
        } else {
            // Display login error message
            // document.getElementById('error-message').innerText = data.detail || 'An error occurred during login.';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle other errors
        // document.getElementById('error-message').innerText = 'An error occurred during login.';
    });
}

const join = function(element) {
    request(element.id);
}

document.querySelectorAll(".join").forEach(element => {
    element.addEventListener("click", () => {
        request(element.id);
    });
});
generate_keys();
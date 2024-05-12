var ws = new WebSocket(`ws://localhost:8000/ws`);
let pyodide
let mySecretNonsence
let bSecretNonsence
let dialer

(async function(){
    pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.20.0/full/",
    });
    generate_keys();
})();

async function rsa(method, msg = "", fKey) {
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

`;
    switch (method){
        case "encrypt":
        case "decrypt":
            code += `RSA.${method}_with_key("${msg}", ${fKey}, 128)`
            break;
        case "generate_keys":
            code += `RSA.${method}()`
            break;
        default:
            console.log("Wrong method");
            return
    }
         

    let result = pyodide.runPython(code);
    // console.log(result);
    return result
}

const generate_keys = async function() {
    if (localStorage.getItem("clientKeys") == null) {
        let result = await rsa("generate_keys");
        localStorage.setItem("clientKeys", result);
    }
}

function generateRandomString(length) {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let randomString = '';
    for (let i = 0; i < length; i++) {
        randomString += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return randomString;
}

function generateSessionKey(min, max) {
    let key = Math.floor(Math.random() * (max - min + 1)) + min;
    localStorage.setItem("sessionKey", key);
    return key;
}

function generateRoomKey(min, max) {
    let key = generateRandomString(16);
    localStorage.setItem("roomKey", key);
    return key;
}

const request = async function(user) {
    return fetch(`http://localhost:8000/kdc/public-key/${user}`, {
      method: 'GET',
    })
    .then(response => response.json()) // Parse response as JSON
    .then(data => {
        if (data) {
            let fKey = JSON.parse(localStorage.getItem("serverPublicKeys"));
            fKey = `(${fKey.e}, ${fKey.n})`;
            return rsa("decrypt", data, fKey = fKey).then(result => {
                return result;
            });
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

const join = async function(user) {
    dialer = user.id
    request(dialer).then(result => {
        let pubB = String(result).split(":")[0];
        pubB = pubB.split(",")[0] + ', ' + 'int(' + pubB.split(",")[1] + ')';
        // console.log(pubB);
        mySecretNonsence = generateRandomString(12);
        rsa(method="encrypt", msg=`${mySecretNonsence}:${localStorage.getItem("username")}`, fKey = pubB).then(result => {
            ws.send(`{"method": "connect", "payload": "${result}", "dest": "${dialer}"}`)
        });
    });
}

const accept = function(payload) {
    console.log("Connection request")
    let fKey = JSON.parse(localStorage.getItem("clientKeys"))
    fKey = `(${fKey.d}, ${fKey.n})`
    rsa(method="decrypt", msg=payload, fKey = fKey).then(result => {
        console.log(result);
        bSecretNonsence = String(result).split(":")[0];
        mySecretNonsence = generateRandomString(12)
        dialer = String(result).split(":")[1];
        request(dialer).then(result => {
            let pubA = String(result).split(":")[0];
            pubA = pubA.split(",")[0] + ', ' + 'int(' + pubA.split(",")[1] + ')';
            // console.log(pubA);
            rsa(method="encrypt", msg=`${bSecretNonsence}:${mySecretNonsence}`, fKey = pubA).then(result => {
                ws.send(`{"method": "confirm", "payload": "${result}", "dest": "${dialer}"}`)
            });
        });
    });
}

const confirm = function(payload) {
    console.log("confirming");
    let fKey = JSON.parse(localStorage.getItem("clientKeys"))
    fKey = `(${fKey.d}, ${fKey.n})`
    rsa(method="decrypt", msg=payload, fKey = fKey).then(result => {
        if (String(result).split(":")[0] == mySecretNonsence) {
            bSecretNonsence = String(result).split(":")[1];
            rsa(method="encrypt", msg=`${bSecretNonsence}:${generateSessionKey(1, 26)}:${generateRoomKey()}`, fKey = pubA).then(result => {
                ws.send(`{"method": "justify", "payload": "${result}", "dest": "${dialer}"}`)
                window.location.href = '/chat';
            });
        }
    });
}

const justify = function(payload) {
    console.log("accepting session key");
    let fKey = JSON.parse(localStorage.getItem("clientKeys"));
    fKey = `(${fKey.d}, ${fKey.n})`;
    rsa(method="decrypt", msg=payload, fKey = fKey).then(result => {
        payload = String(result).split(":");
        if (payload[0] == mySecretNonsence){
            let sessionKey = payload[1];
            let roomKey = payload[2];
            localStorage.setItem("sessionKey", sessionKey);
            localStorage.setItem("roomKey", roomKey);
            window.location.href = '/chat';
        }
    });
}

document.querySelectorAll(".join").forEach(element => {
    element.addEventListener("click", () => {
        join(element);
    });
});

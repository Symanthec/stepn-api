import hashlib
from time import time_ns
from .loginmode import LoginMode


def to_unsigned(x: int, bits: int) -> int:
    """ Zeroes last bit of arbitrary sized number """
    return x & ((1 << bits) - 1)


class PasswordHasher:
    """
        Class for encapsulation of password hashing details.
        (Labeled in JavaScript source code as "C" function)
    """

    __base_seed = 190042800
    __base_code = 'fUi7oEd)IyZcPQlzHDnARm5thFwJKqjgrX2b8VWaOCY9pM!e3TsvkBxNu614LS0G'

    @classmethod
    def hash_password(cls, email: str, password: str, mode: LoginMode) -> str:
        if mode == LoginMode.PASSWORD:
            return cls.__base_token(password, email)
        else:
            return cls.__encode_base64(password, cls.__my_hash_code(email))

    """
    Reverse engineered code from website
    See N::baseToken function
    :param email: Account's E-Mail
    :param password: Account's password
    :param arg3: Hidden parameter, no information
    :return: hash to be sent to server
    """

    @classmethod
    def __encode_base64(cls, source: str, hashcode: int = 0) -> str:
        utf8_bytes = source.encode('utf-8')
        return cls.__en_base64_by_list(utf8_bytes, hashcode)

    @classmethod
    def __base_token(cls, password: str, email: str, arg3: str = 'helloSTEPN') -> str:
        millis = time_ns() // 1000000
        sha_hash = cls.__get_sha256(password + arg3)
        a = sha_hash + '_' + str(millis)
        return cls.__base_encode(a, cls.__my_hash_code(email))

    @classmethod
    def __base_encode(cls, source: str, seed: int = __base_seed) -> str:
        return cls.__encode_base64(source, seed)

    @classmethod
    def __get_sha256(cls, source: str) -> str:
        t = source.encode('utf-8')
        return hashlib.sha256(t).hexdigest()

    @classmethod
    def __my_hash_code(cls, email: str) -> int:
        # Python supports big numbers out-of-the-box
        # StepN, however, operates, using JavaScript library BN.js
        # See https://github.com/indutny/bn.js/ for details

        t = email.encode("utf-8")
        n = 17  # bn.js
        r = t
        i = len(t)
        o = 9223372036854775808  # bn.js
        a = -9223372036854775808  # bn.js
        s = 0

        while s < i:
            u = r[s]
            f = n
            k = 1
            while k < 37:
                n += f
                if n >= 0 and n > o:
                    n = ((n + o) % o) - o
                elif n < 0 and n <= a:
                    n = ((n + a) % a) - a
                k += 1
            n += u
            s += 1

        # 32-bit signed max
        c = 2147483647
        if n >= 0:
            return n & c
        else:
            inverted = ~(-n) & 0xFFFFFFFF
            return (inverted + 1) & c

    @classmethod
    def __en_base64_by_list(cls, byte_arr: bytes, seed: int) -> str:
        if seed > 0:
            byte_arr = cls.__shuffle_positions(byte_arr, seed)

        r = ''
        i = 8 * len(byte_arr)
        o = 0
        while o < i:
            a = 7 & o
            s = o >> 3
            u = 255 & byte_arr[s]
            if a == 0:
                r += cls.__base_code[63 & u]
            else:
                f = u >> a
                s += 1
                if s < len(byte_arr):
                    a = 8 - a
                    u = 255 & byte_arr[s]
                    f |= u << a
                r += cls.__base_code[63 & f]
            o += 6
        return r

    @classmethod
    def __shuffle_positions(cls, byte_arr: bytes, seed: int) -> bytes:
        seed = abs(seed)
        r = bytearray([i for i in range(len(byte_arr))])
        # shuffle byte positions
        r = cls.__shuffle_int_array(r, seed)

        # shuffle original byte array by randomized positions
        o = bytearray([byte_arr[r[a]] for a in range(len(r))])
        return o

    @classmethod
    def __shuffle_int_array(cls, byte_array: bytes, seed: int) -> bytes:
        n = PasswordHasher.Randomizer(seed)
        for r in range(len(byte_array) - 1, -1, -1):
            i = n.next_int_with_bound(r + 1)
            if i != r:
                # swap bytes
                byte_array[i], byte_array[r] = byte_array[r], byte_array[i]
        return byte_array

    class Randomizer:
        """
            Internal class used for the purposes of shuffling bytes in array.
            (Labeled in JavaScript source code as "C" function)
        """

        __seedUniquifier = 8682522807148012
        __multiplier = 25214903917
        __addend = 11
        __mask = 281474976710655

        def __init__(self, new_seed: int):
            self.__seed = new_seed
            self.__seed = self.initial_scramble(new_seed)

        def initial_scramble(self, x: int) -> int:
            return (x ^ self.__multiplier) & self.__mask

        def next(self, t):
            n = (self.__seed * self.__multiplier + self.__addend) & self.__mask
            self.__seed = n
            return to_unsigned(n >> (48 - t), 32)

        def next_int_with_bound(self, t: int) -> int:
            if t <= 0:
                return 0

            n, r, i = None, None, t - 1

            if t & i == 0:
                # check for powers of 2
                o = self.next(31)
                return to_unsigned((o * t) >> 31, 32)

            n = self.next(31)
            r = n % t

            while n - r + i < 0:
                n = self.next(31)
                r = n % t
            return r

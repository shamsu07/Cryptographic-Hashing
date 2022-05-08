import hashlib

class Hash(object):
    """ Common class for all hash methods.
    
    It copies the one of the hashlib module (https://docs.python.org/3.5/library/hashlib.html).
    """
    
    def __init__(self, *args, **kwargs):
        """ Create the Hash object."""
        self.name = self.__class__.__name__  # https://docs.python.org/3.5/library/hashlib.html#hashlib.hash.name
        self.byteorder   = 'little'
        self.digest_size = 0                # https://docs.python.org/3.5/library/hashlib.html#hashlib.hash.digest_size
        self.block_size  = 0                # https://docs.python.org/3.5/library/hashlib.html#hashlib.hash.block_size

    def __str__(self):
        return self.name
        
    def update(self, arg):
        """ Update the hash object with the object arg, which must be interpretable as a buffer of bytes."""
        pass

    def digest(self):
        """ Return the digest of the data passed to the update() method so far. This is a bytes object of size digest_size which may contain bytes in the whole range from 0 to 255."""
        return b""

    def hexdigest(self):
        """ Like digest() except the digest is returned as a string object of double length, containing only hexadecimal digits. This may be used to exchange the value safely in email or other non-binary environments."""
        digest = self.digest()
        raw = digest.to_bytes(self.digest_size, byteorder=self.byteorder)
        format_str = '{:0' + str(2 * self.digest_size) + 'x}'
        return format_str.format(int.from_bytes(raw, byteorder='big'))



class SHA224(Hash):
    """SHA224 hashing, see https://en.wikipedia.org/wiki/SHA-2#Pseudocode."""
    
    def __init__(self):
        self.name        = "SHA224"
        self.byteorder   = 'big'
        self.block_size  = 64
        self.digest_size = 28
        # Note 2: For each round, there is one round constant k[i] and one entry in the message schedule array w[i], 0 ≤ i ≤ 63
        # Note 3: The compression function uses 8 working variables, a through h
        # Note 4: Big-endian convention is used when expressing the constants in this pseudocode,
        #         and when parsing message block data from bytes to words, for example,
        #         the first word of the input message "abc" after padding is 0x61626380

        # Initialize hash values:
        # (The second 32 bits of the fractional parts of the square roots of the 9th through 16th primes 23..53)
        h0 = 0xc1059ed8
        h1 = 0x367cd507
        h2 = 0x3070dd17
        h3 = 0xf70e5939
        h4 = 0xffc00b31
        h5 = 0x68581511
        h6 = 0x64f98fa7
        h7 = 0xbefa4fa4
        
        # Initialize array of round constants:
        # (first 32 bits of the fractional parts of the cube roots of the first 64 primes 2..311):
        self.k = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        ]

        # Store them
        self.hash_pieces = [h0, h1, h2, h3, h4, h5, h6, h7]
    
    def update(self, arg):
        h0, h1, h2, h3, h4, h5, h6, h7 = self.hash_pieces
        # 1. Pre-processing, exactly like MD5
        data = bytearray(arg)
        orig_len_in_bits = (8 * len(data)) & 0xFFFFFFFFFFFFFFFF
        # 1.a. Add a single '1' bit at the end of the input bits
        data.append(0x80)
        # 1.b. Padding with zeros as long as the input bits length ≡ 448 (mod 512)
        while len(data) % 64 != 56:
            data.append(0)
        # 1.c. append original length in bits mod (2 pow 64) to message
        data += orig_len_in_bits.to_bytes(8, byteorder='big')
        assert len(data) % 64 == 0, "Error in padding"
        # 2. Computations
        # Process the message in successive 512-bit = 64-bytes chunks:
        for offset in range(0, len(data), 64):
            # 2.a. 512-bits = 64-bytes chunks
            chunks = data[offset : offset + 64]
            w = [0 for i in range(64)]
            # 2.b. Break chunk into sixteen 32-bit = 4-bytes words w[i], 0 ≤ i ≤ 15
            for i in range(16):
                w[i] = int.from_bytes(chunks[4*i : 4*i + 4], byteorder='big')
            # 2.c.  Extend the first 16 words into the remaining 48
            #       words w[16..63] of the message schedule array:
            for i in range(16, 64):
                s0 = (rightrotate(w[i-15], 7) ^ rightrotate(w[i-15], 18) ^ rightshift(w[i-15], 3)) & 0xFFFFFFFF
                s1 = (rightrotate(w[i-2], 17) ^ rightrotate(w[i-2], 19) ^ rightshift(w[i-2], 10)) & 0xFFFFFFFF
                w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xFFFFFFFF
            # 2.d. Initialize hash value for this chunk
            a, b, c, d, e, f, g, h = h0, h1, h2, h3, h4, h5, h6, h7
            # 2.e. Main loop, cf. https://tools.ietf.org/html/rfc6234
            for i in range(64):
                S1 = (rightrotate(e, 6) ^ rightrotate(e, 11) ^ rightrotate(e, 25)) & 0xFFFFFFFF
                ch = ((e & f) ^ ((~e) & g)) & 0xFFFFFFFF
                temp1 = (h + S1 + ch + self.k[i] + w[i]) & 0xFFFFFFFF
                S0 = (rightrotate(a, 2) ^ rightrotate(a, 13) ^ rightrotate(a, 22)) & 0xFFFFFFFF
                maj = ((a & b) ^ (a & c) ^ (b & c)) & 0xFFFFFFFF
                temp2 = (S0 + maj) & 0xFFFFFFFF

                new_a = (temp1 + temp2) & 0xFFFFFFFF
                new_e = (d + temp1) & 0xFFFFFFFF
                # Rotate the 8 variables
                a, b, c, d, e, f, g, h = new_a, a, b, c, new_e, e, f, g

            # Add this chunk's hash to result so far:
            h0 = (h0 + a) & 0xFFFFFFFF
            h1 = (h1 + b) & 0xFFFFFFFF
            h2 = (h2 + c) & 0xFFFFFFFF
            h3 = (h3 + d) & 0xFFFFFFFF
            h4 = (h4 + e) & 0xFFFFFFFF
            h5 = (h5 + f) & 0xFFFFFFFF
            h6 = (h6 + g) & 0xFFFFFFFF
            h7 = (h7 + h) & 0xFFFFFFFF
        # 3. Conclusion
        self.hash_pieces = [h0, h1, h2, h3, h4, h5, h6, h7]

    def digest(self):
        # h0 append h1 append h2 append h3 append h4 append h5 append h6
        pieces_without_h7 = self.hash_pieces[:-1]
        return sum(leftshift(x, 32 * i) for i, x in enumerate(pieces_without_h7[::-1]))

class SHA512(Hash):
    """SHA384 hashing, see https://en.wikipedia.org/wiki/SHA-2#Pseudocode."""
    
    def __init__(self):
        self.name        = "SHA512"
        self.byteorder   = 'big'
        self.block_size  = 128
        self.digest_size = 64
        # Note 2: For each round, there is one round constant k[i] and one entry in the message schedule array w[i], 0 ≤ i ≤ 79
        # Note 3: The compression function uses 8 working variables, a through h
        # Note 4: Big-endian convention is used when expressing the constants in this pseudocode

        # Initialize hash values:
        # (The second 64 bits of the fractional parts of the square roots of the first 8 primes 2..19)
        h0 = 0x6a09e667f3bcc908
        h1 = 0xbb67ae8584caa73b
        h2 = 0x3c6ef372fe94f82b
        h3 = 0xa54ff53a5f1d36f1
        h4 = 0x510e527fade682d1
        h5 = 0x9b05688c2b3e6c1f
        h6 = 0x1f83d9abfb41bd6b
        h7 = 0x5be0cd19137e2179

        # Initialize array of round constants:
        # (first 64 bits of the fractional parts of the cube roots of the first 80 primes 2..409):
        self.k = [
            0x428a2f98d728ae22, 0x7137449123ef65cd, 0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc, 0x3956c25bf348b538, 
            0x59f111f1b605d019, 0x923f82a4af194f9b, 0xab1c5ed5da6d8118, 0xd807aa98a3030242, 0x12835b0145706fbe, 
            0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2, 0x72be5d74f27b896f, 0x80deb1fe3b1696b1, 0x9bdc06a725c71235, 
            0xc19bf174cf692694, 0xe49b69c19ef14ad2, 0xefbe4786384f25e3, 0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65, 
            0x2de92c6f592b0275, 0x4a7484aa6ea6e483, 0x5cb0a9dcbd41fbd4, 0x76f988da831153b5, 0x983e5152ee66dfab, 
            0xa831c66d2db43210, 0xb00327c898fb213f, 0xbf597fc7beef0ee4, 0xc6e00bf33da88fc2, 0xd5a79147930aa725, 
            0x06ca6351e003826f, 0x142929670a0e6e70, 0x27b70a8546d22ffc, 0x2e1b21385c26c926, 0x4d2c6dfc5ac42aed, 
            0x53380d139d95b3df, 0x650a73548baf63de, 0x766a0abb3c77b2a8, 0x81c2c92e47edaee6, 0x92722c851482353b, 
            0xa2bfe8a14cf10364, 0xa81a664bbc423001, 0xc24b8b70d0f89791, 0xc76c51a30654be30, 0xd192e819d6ef5218, 
            0xd69906245565a910, 0xf40e35855771202a, 0x106aa07032bbd1b8, 0x19a4c116b8d2d0c8, 0x1e376c085141ab53, 
            0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8, 0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb, 0x5b9cca4f7763e373, 
            0x682e6ff3d6b2b8a3, 0x748f82ee5defb2fc, 0x78a5636f43172f60, 0x84c87814a1f0ab72, 0x8cc702081a6439ec, 
            0x90befffa23631e28, 0xa4506cebde82bde9, 0xbef9a3f7b2c67915, 0xc67178f2e372532b, 0xca273eceea26619c, 
            0xd186b8c721c0c207, 0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178, 0x06f067aa72176fba, 0x0a637dc5a2c898a6, 
            0x113f9804bef90dae, 0x1b710b35131c471b, 0x28db77f523047d84, 0x32caab7b40c72493, 0x3c9ebe0a15c9bebc, 
            0x431d67c49c100d4c, 0x4cc5d4becb3e42b6, 0x597f299cfc657e2a, 0x5fcb6fab3ad6faec, 0x6c44198c4a475817
        ]

        # Store them
        self.hash_pieces = [h0, h1, h2, h3, h4, h5, h6, h7]
    
    def update(self, arg):
        h0, h1, h2, h3, h4, h5, h6, h7 = self.hash_pieces
        # 1. Pre-processing, exactly like MD5
        data = bytearray(arg)
        orig_len_in_bits = (8 * len(data)) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        # 1.a. Add a single '1' bit at the end of the input bits
        data.append(0x80)
        # 1.b. Padding with zeros as long as the input bits length ≡ 896 (mod 1024)
        while len(data) % 128 != 112:
            data.append(0)
        # 1.c. append original length in bits mod (2 pow 128) to message
        data += orig_len_in_bits.to_bytes(16, byteorder='big')
        assert len(data) % 128 == 0, "Error in padding"
        # 2. Computations
        # Process the message in successive 1024-bit = 128-bytes chunks:
        for offset in range(0, len(data), 128):
            # 2.a. 1024-bits = 128-bytes chunks
            chunks = data[offset : offset + 128]
            w = [0 for i in range(80)]
            # 2.b. Break chunk into sixteen 128-bit = 8-bytes words w[i], 0 ≤ i ≤ 15
            for i in range(16):
                w[i] = int.from_bytes(chunks[8*i : 8*i + 8], byteorder='big')
            # 2.c.  Extend the first 16 words into the remaining 64
            #       words w[16..79] of the message schedule array:
            for i in range(16, 80):
                s0 = (rightrotate_64(w[i-15], 1) ^ rightrotate_64(w[i-15], 8) ^ rightshift(w[i-15], 7)) & 0xFFFFFFFFFFFFFFFF
                s1 = (rightrotate_64(w[i-2], 19) ^ rightrotate_64(w[i-2], 61) ^ rightshift(w[i-2], 6)) & 0xFFFFFFFFFFFFFFFF
                w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xFFFFFFFFFFFFFFFF
            # 2.d. Initialize hash value for this chunk
            a, b, c, d, e, f, g, h = h0, h1, h2, h3, h4, h5, h6, h7
            # 2.e. Main loop, cf. https://tools.ietf.org/html/rfc6234
            for i in range(80):
                S1 = (rightrotate_64(e, 14) ^ rightrotate_64(e, 18) ^ rightrotate_64(e, 41)) & 0xFFFFFFFFFFFFFFFF
                ch = ((e & f) ^ ((~e) & g)) & 0xFFFFFFFFFFFFFFFF
                temp1 = (h + S1 + ch + self.k[i] + w[i]) & 0xFFFFFFFFFFFFFFFF
                S0 = (rightrotate_64(a, 28) ^ rightrotate_64(a, 34) ^ rightrotate_64(a, 39)) & 0xFFFFFFFFFFFFFFFF
                maj = ((a & b) ^ (a & c) ^ (b & c)) & 0xFFFFFFFFFFFFFFFF
                temp2 = (S0 + maj) & 0xFFFFFFFFFFFFFFFF

                new_a = (temp1 + temp2) & 0xFFFFFFFFFFFFFFFF
                new_e = (d + temp1) & 0xFFFFFFFFFFFFFFFF
                # Rotate the 8 variables
                a, b, c, d, e, f, g, h = new_a, a, b, c, new_e, e, f, g

            # Add this chunk's hash to result so far:
            h0 = (h0 + a) & 0xFFFFFFFFFFFFFFFF
            h1 = (h1 + b) & 0xFFFFFFFFFFFFFFFF
            h2 = (h2 + c) & 0xFFFFFFFFFFFFFFFF
            h3 = (h3 + d) & 0xFFFFFFFFFFFFFFFF
            h4 = (h4 + e) & 0xFFFFFFFFFFFFFFFF
            h5 = (h5 + f) & 0xFFFFFFFFFFFFFFFF
            h6 = (h6 + g) & 0xFFFFFFFFFFFFFFFF
            h7 = (h7 + h) & 0xFFFFFFFFFFFFFFFF
        # 3. Conclusion
        self.hash_pieces = [h0, h1, h2, h3, h4, h5, h6, h7]

    def digest(self):
        # h0 append h1 append h2 append h3 append h4 append h5 append h6 append h7
        return sum(leftshift(x, 64 * i) for i, x in enumerate(self.hash_pieces[::-1]))

def leftrotate(x, c):
    """ Left rotate the number x by c bytes."""
    x &= 0xFFFFFFFF
    return ((x << c) | (x >> (32 - c))) & 0xFFFFFFFF

def rightrotate(x, c):
    """ Right rotate the number x by c bytes."""
    x &= 0xFFFFFFFF
    return ((x >> c) | (x << (32 - c))) & 0xFFFFFFFF

def leftrotate_64(x, c):
    """ Left rotate the number x by c bytes, for 64-bits numbers."""
    x &= 0xFFFFFFFFFFFFFFFF
    return ((x << c) | (x >> (64 - c))) & 0xFFFFFFFFFFFFFFFF

def rightrotate_64(x, c):
    """ Right rotate the number x by c bytes, for 64-bits numbers."""
    x &= 0xFFFFFFFFFFFFFFFF
    return ((x >> c) | (x << (64 - c))) & 0xFFFFFFFFFFFFFFFF

def leftshift(x, c):
    """ Left shift the number x by c bytes."""
    return x << c
def rightshift(x, c):
    """ Right shift the number x by c bytes."""
    return x >> c


def hash_SHA224(data):
    """ Shortcut function to directly receive the hex digest from SHA224(data)."""
    h = SHA224()
    if isinstance(data, str):
        data = bytes(data, encoding='utf8')
    h.update(data)
    return h.hexdigest()

def hash_SHA512(data):
    """ Shortcut function to directly receive the hex digest from SHA512(data)."""
    h = SHA512()
    if isinstance(data, str):
        data = bytes(data, encoding='utf8')
    h.update(data)
    return h.hexdigest()

print("SHA 224: ",hash_SHA224("Hello World"))
print("SHA 512: " ,hash_SHA512("Hello World"))

def true_hash_SHA224(data):
    h = hashlib.sha224()
    if isinstance(data, str):
        data = bytes(data, encoding='utf8')
    h.update(data)
    return h.hexdigest()


def true_hash_SHA512(data):
    h = hashlib.sha512()
    if isinstance(data, str):
        data = bytes(data, encoding='utf8')
    h.update(data)
    return h.hexdigest()


assert hash_SHA224("Hello World") == true_hash_SHA224("Hello World")
assert hash_SHA512("Hello World") == true_hash_SHA512("Hello World")

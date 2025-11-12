import os
import hashlib

# Field prime
p = 2**255 - 19

# Curve parameter d = -121665 / 121666 mod p
def inv(x):
    return pow(x, p-2, p)

d = (-121665 * inv(121666)) % p

# a = -1 for Edwards25519
a = p - 1

# modular square root for p % 8 == 5 (this p satisfies that)
def mod_sqrt(u):
    # Return a square root of u mod p if exists, otherwise None.
    # Uses the algorithm for p % 8 == 5 from RFC.
    
    if u % p == 0:
        return 0
 
    # candidate
    x = pow(u, (p + 3) // 8, p)
    if (x * x - u) % p == 0:
        return x
 
    # try x = x * 2^((p-1)/4)
    I = pow(2, (p - 1) // 4, p)
    x = (x * I) % p
    if (x * x - u) % p == 0:
        return x
    return None

# base point: y = 4/5, x = sqrt((y^2 - 1) / (d*y^2 + 1))
By = (4 * inv(5)) % p

# compute Bx
num = (By * By - 1) % p
den = (d * By * By + 1) % p
Bx = mod_sqrt((num * inv(den)) % p)

if Bx is None:
    raise RuntimeError("failed to compute basepoint x")

# choose positive x 
# RFC uses the x whose least significant bit is 0? We can pick whichever; encoding will set sign bit.
# We will use the value that results from mod_sqrt — both +/- are valid.

B = (Bx % p, By % p)

# point addition (Edwards coordinates), points are tuples (x,y)

def ed_add(P, Q):
    (x1, y1), (x2, y2) = P, Q
    x1x2 = (x1 * x2) % p
    y1y2 = (y1 * y2) % p
    xnum = (x1 * y2 + x2 * y1) % p
    xden = (1 + d * x1x2 * y1y2) % p
    ynum = (y1y2 - a * x1x2) % p
    yden = (1 - d * x1x2 * y1y2) % p
    x3 = (xnum * inv(xden)) % p
    y3 = (ynum * inv(yden)) % p

    return (x3, y3)

def ed_double(P):
    return ed_add(P, P)

# scalar multiplication (double-and-add)

def scalarmult(P, e):
    # e is Python int
    Q = (0, 1)  # identity point
    R = P
    while e > 0:
        if e & 1:
            Q = ed_add(Q, R)
        R = ed_double(R)
        e >>= 1
    return Q

# compress point: encode y (little-endian 32 bytes) and sign bit of x in msb

def encodepoint(P):
    x, y = P
    y_bytes = int.to_bytes(y, 32, "little")
    x_lsb = x & 1

    # set highest bit of last byte to x_lsb

    last = y_bytes[-1]
    last = (last & 0x7F) | (x_lsb << 7)
    y_bytes = y_bytes[:-1] + bytes([last])

    return y_bytes

# clamp the 32-byte scalar as RFC8032 says

def clamp_scalar(h_bytes32):
    hb = bytearray(h_bytes32)

    hb[0] &= 248
    hb[31] &= 127
    hb[31] |= 64

    return int.from_bytes(hb, "little")

def generate_keypair():

    # seed (32 bytes random)
    seed = os.urandom(32)

    # H = SHA-512(seed)
    h = hashlib.sha512(seed).digest()

    # a = clamp(H[:32])
    a = clamp_scalar(h[:32])

    # A = a * B  (scalar multiply)
    A = scalarmult(B, a)

    # public key = encodepoint(A)
    public_key = encodepoint(A)

    # return seed (private seed) and public key
    # commonly private key bytes are seed || public_key; but we'll return both separately

    return seed, public_key

# only takes in raw bytes, NOT hex strings ("abc123..")
def verify_keypair(keypair):    # takes in a tuple (seed, public_key) or a 64 byte concentrated key (seed + public_key) 
    if isinstance(keypair, tuple):
        seed, pub = keypair
    elif isinstance(keypair, (bytes, bytearray)) and len(keypair) == 64:
        seed, pub = keypair[:32], keypair[32:]
    else:
        raise ValueError("function only takes in a tuple or a 64 byte concentrated key")

    h = hashlib.sha512(seed).digest()
    a = clamp_scalar(h[:32])

    A = scalarmult(B, a)
    derived_pub = encodepoint(A)

    return derived_pub == pub
    # returns True if valid, false otherwise.

def keygen():
    sk_seed, pk = generate_keypair()

    public_key = pk.hex()
    private_key = (sk_seed + pk).hex()

    valid_status = verify_keypair((sk_seed, pk))

    return sk_seed, public_key, private_key, valid_status



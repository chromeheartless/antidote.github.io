import math

# --------------------
# Reed-Solomon helpers
# --------------------
EXP = [1]*512
LOG = [0]*256
for i in range(1, 256):
    EXP[i] = EXP[i-1] * 2
    if EXP[i] >= 256:
        EXP[i] ^= 0x11d
for i in range(255):
    LOG[EXP[i]] = i
for i in range(255, 512):
    EXP[i] = EXP[i-255]

def gf_mul(x, y):
    if x == 0 or y == 0:
        return 0
    return EXP[LOG[x]+LOG[y]]

def rs_poly_mul(p1, p2):
    res = [0]*(len(p1)+len(p2)-1)
    for i in range(len(p1)):
        for j in range(len(p2)):
            res[i+j] ^= gf_mul(p1[i], p2[j])
    return res

def rs_generate(data, nsym):
    poly = [1]
    for _ in range(nsym):
        poly = rs_poly_mul(poly, [1, 1])
    res = data[:]
    res += [0]*nsym
    for i in range(len(data)):
        coef = res[i]
        if coef != 0:
            for j in range(len(poly)):
                res[i+j] ^= gf_mul(poly[j], coef)
    return res[-nsym:]

# --------------------
# Byte mode encoding
# --------------------
def encode_byte(data):
    bits = "0100"  # byte mode indicator
    bits += format(len(data), "08b")  # character count (version 1)
    for c in data:
        bits += format(ord(c), "08b")
    return bits

def finalize_bits(bits, length):
    bits += "0000"  # terminator
    while len(bits) % 8 != 0:
        bits += "0"
    pad_bytes = [0xec, 0x11]
    i = 0
    while len(bits)//8 < length:
        bits += format(pad_bytes[i%2], "08b")
        i += 1
    return bits

# --------------------
# QR matrix
# --------------------
SIZE = 21  # version 1

def make_matrix():
    return [[0 for _ in range(SIZE)] for _ in range(SIZE)]

def add_finder(matrix, x, y):
    for i in range(-1,8):
        for j in range(-1,8):
            if 0 <= x+i < SIZE and 0 <= y+j < SIZE:
                if 0<=i<=6 and 0<=j<=6 and (i in [0,6] or j in [0,6] or (2<=i<=4 and 2<=j<=4)):
                    matrix[y+j][x+i] = 1
                else:
                    matrix[y+j][x+i] = 0

def fill_data(matrix, data_bits):
    dir_up = True
    x = SIZE-1
    y = SIZE-1
    i = 0
    while x > 0:
        if x == 6: x -= 1  # skip vertical timing
        for _ in range(SIZE):
            for dx in [0, -1]:
                if matrix[y][x+dx] == 0:
                    if i < len(data_bits):
                        matrix[y][x+dx] = int(data_bits[i])
                        i += 1
            y = y-1 if dir_up else y+1
        dir_up = not dir_up
        x -= 2

# --------------------
# Add quiet zone
# --------------------
def add_quiet_zone(matrix, size=4):
    old_size = len(matrix)
    new_size = old_size + 2*size
    new_matrix = [[0]*new_size for _ in range(new_size)]
    for y in range(old_size):
        for x in range(old_size):
            new_matrix[y+size][x+size] = matrix[y][x]
    return new_matrix

# --------------------
# Main QR generator
# --------------------
def generate_qr_ascii(data, return_string=False):
    bits = encode_byte(data)
    bits = finalize_bits(bits, 19)  # version 1-L has 19 bytes
    data_bytes = [int(bits[i:i+8],2) for i in range(0,len(bits),8)]
    ecc = rs_generate(data_bytes, 7)
    final_bits = "".join(format(b, "08b") for b in data_bytes + ecc)

    matrix = make_matrix()
    add_finder(matrix, 0,0)
    add_finder(matrix, SIZE-7,0)
    add_finder(matrix, 0,SIZE-7)
    fill_data(matrix, final_bits)

    matrix = add_quiet_zone(matrix, size=4)  # add margin for phone readability

    qr_str = "\n".join("".join("██" if c else "  " for c in row) for row in matrix)

    if return_string:
        return qr_str
    else:
        print(qr_str)

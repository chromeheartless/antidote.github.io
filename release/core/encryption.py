import os
import time
import random
import hashlib
from .ed25519 import keygen


# --- encryption section ---

def get_ssn(message_sender_public_key):
    return message_sender_public_key[:12]

def generate_keypair():
    seed, public_key, private_key, valid_status = keygen()
    return seed, public_key, private_key, valid_status

# --- encryption section ---


def generate_keystream(key, length):
    seed = int(hashlib.sha256(key.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    return [rng.randint(0, 255) for _ in range(length)]

def encrypt(message_sender_public_key, message_receiver_public_key, message_content):
    msg_bytes = message_content.encode('utf-8')
    keystream = generate_keystream(message_receiver_public_key, len(msg_bytes))
    encrypted_bytes = bytes([b ^ k for b, k in zip(msg_bytes, keystream)])
    return encrypted_bytes.hex() # safe for printing/storage

    # add encrypt with private key; linked into pub so client side part works
def decrypt_with_priv(encrypted_hex, message_receiver_private_key):
    pass
    # derrive the public key from the private key

    # decrypt_with_pub(encrypted_hex, receiver_public_key)ö

def decrypt_with_pub(encrypted_hex, receiver_public_key):
    try:
        encrypted_bytes = bytes.fromhex(encrypted_hex)
    except ValueError:
        raise ValueError("Encrypted text is not valid hex.")

    keystream = generate_keystream(receiver_public_key, len(encrypted_bytes))
    decrypted_bytes = bytes([b ^ k for b, k in zip(encrypted_bytes, keystream)])
    try:
        return decrypted_bytes.decode('utf-8')
    except UnicodeDecodeError:
        # If decode fails, return raw bytes so user can inspect
        return decrypted_bytes


# --- signature section ---


def sign(message_sender_public_key, message_receiver_public_key, message):
    sender_public_key_cut_size = 8
    receiver_public_key_cut_size = 8
    
    part1_key_sig = ''
    part2_key_sig = ''

    for _ in range(sender_public_key_cut_size):
        index = ord(os.urandom(1)) % len(message_sender_public_key)
        part1_key_sig += message_sender_public_key[index]

    for _ in range(receiver_public_key_cut_size):
        index = ord(os.urandom(1)) % len(message_receiver_public_key)
        part2_key_sig += message_receiver_public_key[index]

    hashed_signature = hashlib.sha256((part1_key_sig + part2_key_sig).encode('utf-8')).hexdigest()
    content_signature = hashlib.sha256(message.encode('utf-8')).hexdigest()

    return hashed_signature, content_signature

def check_integrity(message):
    return True

import hashlib

def generate_key_from_string(key_str, length):
    """Turn a string key into a fixed-length byte key"""
    hash_bytes = hashlib.sha256(key_str.encode()).digest()
    return hash_bytes[:length]

def encrypt(message, receiver_key):
    key = generate_key_from_string(receiver_key, len(message))
    encrypted = ''.join(chr(ord(c) ^ k) for c, k in zip(message, key))
    return encrypted

def decrypt(encrypted_message, receiver_key):
    # XOR again with same key to get original
    return encrypt(encrypted_message, receiver_key)

# Example usage
receiver_key = "receiver_secret_key"
message = "wait ssssswhat"
encrypted_msg = encrypt(message, receiver_key)
print("Encrypted:", encrypted_msg)

decrypted_msg = decrypt(encrypted_msg, receiver_key)
print("Decrypted:", decrypted_msg)

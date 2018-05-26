import hashlib

def crypto_hash(msg):
    return hashlib.sha256(msg).hexdigest()

def crypto_hash_double(msg):
    return crypto_hash(crypto_hash(msg).encode())


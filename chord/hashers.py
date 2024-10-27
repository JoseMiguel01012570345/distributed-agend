from hashlib import sha1

def sha1_hash(obj,bits_memory):
    hasher = sha1()
    hasher.update(bytes(obj,'utf-8'))
    return int(hasher.hexdigest(),16) % 2**bits_memory
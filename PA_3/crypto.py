from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

delim = '++++'


def load_public_key(filename):
    with open(filename, "rb") as pem_in:
        pemlines = pem_in.read()
    public_key = serialization.load_pem_public_key(pemlines, default_backend())
    return public_key


def load_private_key(filename):
    with open(filename, "rb") as pem_in:
        pemlines = pem_in.read()
    private_key = serialization.load_pem_private_key(
        pemlines, None, default_backend())
    return private_key


# Read bob public key from disk
bPublicKey = load_public_key('/home/u0726408/cs4480/CS4480/PA_3/keys/bobPublic.pem')
bPublicKey_bytes = bPublicKey.public_bytes(encoding=serialization.Encoding.PEM,
                                           format=serialization.PublicFormat.SubjectPublicKeyInfo)
# Hash bob public with sha1
bob_hash = hashes.Hash(hashes.SHA1())
bob_hash.update(bPublicKey_bytes)
final_hash = bob_hash.finalize()
print(bob_hash)
# Encrypt ^ with c private key (from disk)
cPublicKey = load_public_key('/home/u0726408/cs4480/CS4480/PA_3/keys/cPublic.pem')
# cPrivateKey_bytes = cPrivateKey.private_bytes(encoding=serialization.Encoding.PEM,
#                                               format=serialization.PublicFormat.SubjectPublicKeyInfo)
encryption = cPublicKey.encrypt(final_hash, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))
print(encryption)
# # Bob sends public key KC-(H(KB+)), KB+

# Verification from Alice ****
# Extract public key after delimeter
# Alice takes encrypted msg, decrypt with c public key (from disk)
# "unsha" the inner part with sha1
# Result is bob public key (can compare with delimited part)

# Request user input for msg
# Hash msg with sha1
# Read Alice private key from disk
# Encrypt new hash with Alic private key
# Combine msg with ^
# Encrypt ^ with AES key --- store as A
# Encrypt AES key with Bob public key --- store as B
# Concatonate A, B

# Break up A,B
# DO B FIRST: Decrypt AES key with Bob's private key
# Save AES key
# NOW DO A: Decrypt A with AES key (split into msg, KA-(H(m)))
# Bob gets Alic public key from disk
# Decrypts second part of delimeted data with Alice public key
# "unsha" ^
# compare ^ with received msg
# if match, display

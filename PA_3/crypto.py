from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

delim = bytearray(b'+++++')


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
#bPublicKey = load_public_key('keys\\bobPublic.pem')
bPublicKey_bytes = bytearray(bPublicKey.public_bytes(encoding=serialization.Encoding.PEM,
                                           format=serialization.PublicFormat.SubjectPublicKeyInfo))
raw_b_public_key = bytes(bPublicKey_bytes)

# Sign ^ with c private key (from disk)
cPrivateKey = load_private_key('/home/u0726408/cs4480/CS4480/PA_3/keys/cPrivate.pem')
#cPrivateKey = load_private_key('keys\\cPrivate.pem')
#b_sig = bytearray(cPrivateKey.sign(final_hash, padding.PSS(mgf=padding.MGF1(algorithm=hashes.SHA1()),salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1()))
b_sig = bytearray(cPrivateKey.sign(raw_b_public_key, padding.PSS(mgf=padding.MGF1(algorithm=hashes.SHA1()),salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1()))
bob_msg_arr = b_sig+delim+bPublicKey_bytes
bob_msg = bytes(bob_msg_arr)
# ****** Send bob message *****

# Verification from Alice ****
# Extract public key after delimeter
split_b_msg = bob_msg.split(b'+++++')
recv_b_key = split_b_msg[1]
recv_b_sig = split_b_msg[0]

# Alice takes encrypted msg, decrypt with c public key (from disk)
cPublicKey = load_public_key('/home/u0726408/cs4480/CS4480/PA_3/keys/cPublic.pem')
#cPublicKey = load_public_key('keys\\cPublic.pem')
try:
    aVerify = cPublicKey.verify(recv_b_sig,recv_b_key,padding.PSS(mgf=padding.MGF1(hashes.SHA1()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA1())
except:
    print("Verification failed for received message")
    exit()

# Result is bob public key (can compare with delimited part)
formatted_b_key = serialization.load_pem_public_key(recv_b_key, default_backend())
print(formatted_b_key)

# Request user input for msg
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
# compare ^ with received msg
# if match, display

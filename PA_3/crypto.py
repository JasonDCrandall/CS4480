import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

delim = bytearray(b'++++++++++')


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


# ******** BOB *********
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
b_sig = bytearray(cPrivateKey.sign(raw_b_public_key, padding.PSS(mgf=padding.MGF1(
    algorithm=hashes.SHA1()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1()))
bob_msg_arr = b_sig+delim+bPublicKey_bytes
bob_msg = bytes(bob_msg_arr)
# ****** Send bob message *****


# ********** Alice **********
# Verification from Alice ****
# Extract public key after delimeter
split_b_msg = bob_msg.split(b'++++++++++')
recv_b_key = split_b_msg[1]
recv_b_sig = split_b_msg[0]

# Alice takes encrypted msg, decrypt with c public key (from disk)
cPublicKey = load_public_key('/home/u0726408/cs4480/CS4480/PA_3/keys/cPublic.pem')
#cPublicKey = load_public_key('keys\\cPublic.pem')
try:
    aVerify = cPublicKey.verify(recv_b_sig, recv_b_key, padding.PSS(mgf=padding.MGF1(
        hashes.SHA1()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1())
except:
    print("Verification failed for received message")
    exit()

# Result is bob public key (can compare with delimited part)
formatted_b_key = serialization.load_pem_public_key(
    recv_b_key, default_backend())

# Request user input for msg
string_message = "This is a test message"
message = string_message.encode()
byteMessage = bytearray(message)

# Read Alice private key from disk
aPrivateKey = load_private_key('/home/u0726408/cs4480/CS4480/PA_3/keys/alicePrivate.pem')
#aPrivateKey = load_private_key('keys\\alicePrivate.pem')

# Encrypt new hash with Alic private key
a_sig = bytearray(aPrivateKey.sign(message, padding.PSS(mgf=padding.MGF1(
    algorithm=hashes.SHA1()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1()))

# Combine msg with ^
a_msg_arr = a_sig+delim+byteMessage
a_msg = bytes(a_msg_arr)
print(a_msg)

# Encrypt ^ with AES key --- store as A
ks = bytearray(os.urandom(32))
raw_ks = bytes(ks)
iv = b'a' * 16 # This is the initialization vector
cipher = Cipher(algorithms.AES(raw_ks), modes.CBC(iv), default_backend())
encryptor = cipher.encryptor()
a_alice_encryption = bytearray(encryptor.update(a_msg))
raw_a_alice_encryption = bytes(a_alice_encryption)
print(raw_a_alice_encryption)

# Encrypt AES key with Bob public key --- store as B
b_alice_encryption = bytearray(formatted_b_key.encrypt(raw_ks, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None)))

# Concatonate A, B
full_a_msg = a_alice_encryption+delim+b_alice_encryption
raw_full_a_msg = bytes(full_a_msg)


# ********* BOB *************
# Break up A,B
split_a_msg = raw_full_a_msg.split(b'++++++++++')
first_e = split_a_msg[0]
second_e = split_a_msg[1]
print(first_e)

# DO B FIRST: Decrypt AES key with Bob's private key
bPrivateKey = load_private_key('/home/u0726408/cs4480/CS4480/PA_3/keys/bobPrivate.pem')
#bPrivateKey = load_private_key('keys\\bobPrivate.pem')
aes_key = bPrivateKey.decrypt(second_e,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))

# NOW DO A: Decrypt A with AES key (split into msg, KA-(H(m)))
biv = b'a' * 16
decipher = Cipher(algorithms.AES(aes_key), modes.CBC(biv), default_backend())
decryptor = decipher.decryptor()
unencrypted_packet = decryptor.update(first_e)
print(unencrypted_packet)
# Bob gets Alic public key from disk
aPublicKey = load_public_key('/home/u0726408/cs4480/CS4480/PA_3/keys/alicePublic.pem')
#aPublicKey = load_public_key('keys\\alicePublic.pem')

# Decrypts second part of delimeted data with Alice public key
split_hash = unencrypted_packet.split(b'++++++++++')
a_hash = split_hash[0]
msg = split_hash[1]

try:
    recv_msg = aPublicKey.verify(a_hash,msg,padding.PSS(mgf=padding.MGF1(algorithm=hashes.SHA1()),salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1())
except:
    print("Unable to verify Alice's message")

print(msg)
# if match, display

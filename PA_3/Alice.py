# Code representing alice in the secure text transfer
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as p
from socket import *
import json

HOST = "localhost"
BPORT = 3344
APORT = 4455
delim = bytearray(b'++++++++++')
# Below are the steps needed from Alice's side of the program:

def main():
    bobInfo = requestBobsKey()
    msg = buildMessage(bobInfo)
    sendMsgToBob(msg)


# Request and verify Bob's public Key
def requestBobsKey():
    with socket(AF_INET, SOCK_STREAM) as s:
        try:
            s.connect((HOST, BPORT))
        except:
            print(f"Bob failed to respond.")
            return
        command = {
            "command":"requestKey"
        }
        print('Sending Command: ',command)
        s.send(json.dumps(command).encode())
        data = s.recv(1024)
        return data
        
def buildMessage(bob_msg):
    # ********** Alice **********
    # Verification from Alice ****
    # Extract public key after delimeter
    split_b_msg = bob_msg.split(b'++++++++++')
    recv_b_key = split_b_msg[1]
    recv_b_sig = split_b_msg[0]

    # Alice takes encrypted msg, decrypt with c public key (from disk)
    cPublicKey = load_public_key('/home/u0726408/cs4480/CS4480/PA_3/keys/cPublic.pem')
    try:
        aVerify = cPublicKey.verify(recv_b_sig, recv_b_key, padding.PSS(mgf=padding.MGF1(
            hashes.SHA1()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1())
    except:
        print("Verification failed for received message")
        exit()

    # Result is bob public key (can compare with delimited part)
    formatted_b_key = serialization.load_pem_public_key(
        recv_b_key, default_backend())

    # Print message to send to bob
    string_message = "This is a test message with text"
    print('Sending to bob: ', string_message)
    message = string_message.encode()
    byteMessage = bytearray(message)

    # Read Alice private key from disk
    aPrivateKey = load_private_key('/home/u0726408/cs4480/CS4480/PA_3/keys/alicePrivate.pem')

    # Encrypt new hash with Alic private key
    a_sig = bytearray(aPrivateKey.sign(message, padding.PSS(mgf=padding.MGF1(
        algorithm=hashes.SHA1()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1()))

    # Combine msg with ^
    a_msg_arr = a_sig+delim+byteMessage
    a_msg = bytes(a_msg_arr)
    padder = p.PKCS7(128).padder()
    padded_a = padder.update(a_msg) + padder.finalize()

    # Encrypt ^ with AES key --- store as A
    ks = bytearray(os.urandom(32))
    raw_ks = bytes(ks)
    iv = b'a' * 16 # This is the initialization vector
    cipher = Cipher(algorithms.AES(raw_ks), modes.CBC(iv), default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_a) + encryptor.finalize()

    a_alice_encryption = bytearray(ct)
    raw_a_alice_encryption = bytes(a_alice_encryption)

    # Encrypt AES key with Bob public key --- store as B
    b_alice_encryption = bytearray(formatted_b_key.encrypt(raw_ks, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None)))

    # Concatonate A, B
    full_a_msg = a_alice_encryption+delim+b_alice_encryption
    raw_full_a_msg = bytes(full_a_msg)

    return raw_full_a_msg

def sendMsgToBob(msg):
    with socket(AF_INET, SOCK_STREAM) as s:
        try:
            s.connect((HOST, BPORT))
        except:
            print(f"Bob failed to respond.")
            return
        print('Sending Message')
        s.send(msg)

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


if __name__ == "__main__":
    main()
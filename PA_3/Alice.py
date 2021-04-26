# Code representing alice in the secure text transfer.
# Requests Bob's public key, then encrypts a text message inputed from the user
# to send back to bob that is signed with Alice's private key.
# 
# By Jason Crandall u0726408

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

def main():
    bobInfo = requestBobsKey()
    msg = buildMessage(bobInfo)
    sendMsgToBob(msg)


def requestBobsKey():
    # Connect to bob and request his key
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
    # Split receivd data into key and signature
    split_b_msg = bob_msg.split(b'++++++++++')
    recv_b_key = split_b_msg[1]
    recv_b_sig = split_b_msg[0]

    # Takes signature, varify with c public key
    cPublicKey = load_public_key('keys/cPublic.pem')
    try:
        print("Verifying bob's key")
        aVerify = cPublicKey.verify(recv_b_sig, recv_b_key, padding.PSS(mgf=padding.MGF1(
            hashes.SHA1()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1())
    except:
        print("Verification failed for received message")
        exit()

    # Serialize and store Bob's public key
    formatted_b_key = serialization.load_pem_public_key(
        recv_b_key, default_backend())

    # Retrieve message to send from user
    string_message = input("Enter a message to send to Bob: ")
    message = string_message.encode()
    byteMessage = bytearray(message)

    # Sign new message with Alice's private key and hash with SHA1
    aPrivateKey = load_private_key('keys/alicePrivate.pem')
    a_sig = bytearray(aPrivateKey.sign(message, padding.PSS(mgf=padding.MGF1(
        algorithm=hashes.SHA1()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1()))

    # Concatonate signature with message and pad to fit block size
    a_msg_arr = a_sig+delim+byteMessage
    a_msg = bytes(a_msg_arr)
    padder = p.PKCS7(128).padder()
    padded_a = padder.update(a_msg) + padder.finalize()

    # Encrypt concatonation with AES key --- store as first part of message to send
    ks = bytearray(os.urandom(32))
    raw_ks = bytes(ks)
    iv = b'a' * 16 # This is the initialization vector
    cipher = Cipher(algorithms.AES(raw_ks), modes.CBC(iv), default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_a)

    a_alice_encryption = bytearray(ct)

    # Encrypt AES key with Bob public key --- store as secondpart of the message to send
    b_alice_encryption = bytearray(formatted_b_key.encrypt(raw_ks, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None)))

    # Concatonate first and second pieces and return
    full_a_msg = a_alice_encryption+delim+b_alice_encryption
    raw_full_a_msg = bytes(full_a_msg)

    return raw_full_a_msg


def sendMsgToBob(msg):
    # Connect to bob and send newly formed message
    with socket(AF_INET, SOCK_STREAM) as s:
        try:
            s.connect((HOST, BPORT))
        except:
            print(f"Bob failed to respond.")
            return
        print('Sending Message')
        s.send(msg)


# Helper method that serializes a stored public key
def load_public_key(filename):
    with open(filename, "rb") as pem_in:
        pemlines = pem_in.read()
    public_key = serialization.load_pem_public_key(pemlines, default_backend())
    return public_key

# Helper method that serializes a stored private key
def load_private_key(filename):
    with open(filename, "rb") as pem_in:
        pemlines = pem_in.read()
    private_key = serialization.load_pem_private_key(
        pemlines, None, default_backend())
    return private_key


if __name__ == "__main__":
    main()
# Code representing Bob in the secure text transfer.
# Sends public key to Alice and waits for a message.
# Once received, it will verify and decrypt the message to display
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

delim = bytearray(b'++++++++++')
HOST = 'localhost'
PORT = 3344

def main():
    # Start server code to listen for Alice
    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(2)
        # Listen for incoming messages
        while True:
            connection, addr = s.accept()
            with connection:
                data = connection.recv(1024)
                command = ''
                try:
                    jsonData = json.loads(data.decode())
                    command = jsonData["command"]
                except:
                    command = data
                if(command == "requestKey"):
                    key_msg = getKeyInfo()
                    print("Sending key to Alice")
                    connection.send(key_msg)
                else:
                    msg = decryptMsg(command)
                    print("Received message from Alice:",msg.decode())
                    exit()




def getKeyInfo():
    # Read bob's public key from key file
    bPublicKey = load_public_key('keys/bobPublic.pem')
    bPublicKey_bytes = bytearray(bPublicKey.public_bytes(encoding=serialization.Encoding.PEM,
                                                        format=serialization.PublicFormat.SubjectPublicKeyInfo))
    raw_b_public_key = bytes(bPublicKey_bytes)

    # Sign the key with c private key (from key file)
    cPrivateKey = load_private_key('keys/cPrivate.pem')
    b_sig = bytearray(cPrivateKey.sign(raw_b_public_key, padding.PSS(mgf=padding.MGF1(
        algorithm=hashes.SHA1()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1()))

    # Concatonate signature with key and return
    bob_msg_arr = b_sig+delim+bPublicKey_bytes
    bob_msg = bytes(bob_msg_arr)
    return bob_msg



def decryptMsg(raw_full_a_msg):
    # Break up received message into the separate encryptions
    split_a_msg = raw_full_a_msg.split(b'++++++++++')
    first_e = split_a_msg[0]
    second_e = split_a_msg[1]

    # Decrypt AES key with Bob's private key
    bPrivateKey = load_private_key('keys/bobPrivate.pem')
    aes_key = bPrivateKey.decrypt(second_e,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))

    # Decrypt A with AES key (split into msg, KA-(H(m)))
    biv = b'a' * 16
    decipher = Cipher(algorithms.AES(aes_key), modes.CBC(biv), default_backend())
    decryptor = decipher.decryptor()
    unencrypted_packet = decryptor.update(first_e)
    unpadder = p.PKCS7(128).unpadder()
    unpadded_packet = unpadder.update(unencrypted_packet) + unpadder.finalize()

    # Bob gets Alice public key from file
    aPublicKey = load_public_key('keys/alicePublic.pem')

    # Decrypts second part of delimeted data with Alice public key
    split_hash = unpadded_packet.split(b'++++++++++')
    a_hash = split_hash[0]
    msg = split_hash[1]

    # Verify the message with Alice Public key and print if verification is successful
    try:
        print("Verifying Alice's Signature")
        recv_msg = aPublicKey.verify(a_hash,msg,padding.PSS(mgf=padding.MGF1(algorithm=hashes.SHA1()),salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1())
    except:
        print("Unable to verify Alice's message")
        exit()
    
    return msg

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
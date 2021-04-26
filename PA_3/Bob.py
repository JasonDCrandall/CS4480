# Code representing Bob in the secure text transfer
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from socket import *
import json

delim = bytearray(b'++++++++++')
HOST = 'localhost'
PORT = 3344

def main():
    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(2)
        # Listen for incoming messages
        while True:
            connection, addr = s.accept()
            with connection:
                data = connection.recv(1024)
                command = ''
                # Ensure the correct format is received
                try:
                    jsonData = json.loads(data.decode())
                    command = jsonData["command"]
                except:
                    command = data
                if(command == "requestKey"):
                    key_msg = getKeyInfo()
                    connection.send(key_msg)
                else:
                    msg = decryptMsg(command)
                    print("Received message from Alice: ",msg.decode())
                    exit()

def getKeyInfo():
    # ******** BOB *********
    # Read bob public key from disk
    bPublicKey = load_public_key('/home/u0726408/cs4480/CS4480/PA_3/keys/bobPublic.pem')
    bPublicKey_bytes = bytearray(bPublicKey.public_bytes(encoding=serialization.Encoding.PEM,
                                                        format=serialization.PublicFormat.SubjectPublicKeyInfo))
    raw_b_public_key = bytes(bPublicKey_bytes)

    # Sign ^ with c private key (from disk)
    cPrivateKey = load_private_key('/home/u0726408/cs4480/CS4480/PA_3/keys/cPrivate.pem')
    #b_sig = bytearray(cPrivateKey.sign(final_hash, padding.PSS(mgf=padding.MGF1(algorithm=hashes.SHA1()),salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1()))
    b_sig = bytearray(cPrivateKey.sign(raw_b_public_key, padding.PSS(mgf=padding.MGF1(
        algorithm=hashes.SHA1()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1()))
    bob_msg_arr = b_sig+delim+bPublicKey_bytes
    bob_msg = bytes(bob_msg_arr)
    return bob_msg

def decryptMsg(raw_full_a_msg):
    # ********* BOB *************
    # Break up A,B
    split_a_msg = raw_full_a_msg.split(b'++++++++++')
    first_e = split_a_msg[0]
    second_e = split_a_msg[1]

    # DO B FIRST: Decrypt AES key with Bob's private key
    bPrivateKey = load_private_key('/home/u0726408/cs4480/CS4480/PA_3/keys/bobPrivate.pem')
    aes_key = bPrivateKey.decrypt(second_e,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(),label=None))

    # NOW DO A: Decrypt A with AES key (split into msg, KA-(H(m)))
    biv = b'a' * 16
    decipher = Cipher(algorithms.AES(aes_key), modes.CBC(biv), default_backend())
    decryptor = decipher.decryptor()
    unencrypted_packet = decryptor.update(first_e)

    # Bob gets Alic public key from disk
    aPublicKey = load_public_key('/home/u0726408/cs4480/CS4480/PA_3/keys/alicePublic.pem')

    # Decrypts second part of delimeted data with Alice public key
    split_hash = unencrypted_packet.split(b'++++++++++')
    a_hash = split_hash[0]
    msg = split_hash[1]

    try:
        recv_msg = aPublicKey.verify(a_hash,msg,padding.PSS(mgf=padding.MGF1(algorithm=hashes.SHA1()),salt_length=padding.PSS.MAX_LENGTH), hashes.SHA1())
    except:
        print("Unable to verify Alice's message")
        exit()
    
    return msg

    

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
# Below are the basic steps for Bob's side of the program:

# Provide public key with signed msg digest

# Wait

# Receeive secure data from Alice

# Use crypto lib to inverse Alice's msg and print

# End

if __name__ == "__main__":
    main()
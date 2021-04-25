# Code for generating the public and private keys needed for the program

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

def generateKeys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM, 
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption())

    public_pem = private_key.public_key().public_bytes(encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo)

    keys = [private_pem, public_pem]
    return keys

a = generateKeys()
b = generateKeys()
c = generateKeys()

def writeFile(filename, data):
    with open(f"keys\\{filename}Public.pem", "wb") as public:
        publicKey = data[1]
        public.write(publicKey)
    with open(f"keys\\{filename}Private.pem", "wb") as private:
        privateKey = data[0]
        private.write(privateKey) 

writeFile("alice",a)
writeFile("bob",b)
writeFile("c", c)
# Code for generating the public and private keys needed for the program

from cryptography.hazmat.primitives.asymmetric import rsa

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
print(private_key, private_key.public_key())




# from Crypto.PublicKey import RSA

# Akey = RSA.generate(2048)
# a_public = Akey.publickey().exportKey("PEM")
# a_private = Akey.exportKey("PEM")
# print(a_private, a_public)
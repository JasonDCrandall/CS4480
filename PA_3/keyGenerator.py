# Code for generating the public and private keys needed for the program

from Crypto.PublicKey import RSA

Akey = RSA.generate(2048)
a_public = Akey.publickey().exportKey("PEM")
a_private = Akey.exportKey("PEM")
print(a_private, a_public)
# This is the node in the network that will generate 100 messages 
# containing 512 bytes of data each. Once generated, it will send 
# the packets to node B, which will be approved by the router R.
#
# Created By: Jason Crandall u0726408

from socket import *
import json
import sys
import random

HOST = 'localhost'
ROUTER = 3333
msgArr = []

def main():
    # Generate an array of messages to send to the router
    generateMessages()
    # Send messages to router
    sendToRouter()

def generateMessages():
    global msgArr
    # Loop and create a series of messages to append to the global arr
    count = 0
    while (count < 100):
        #TODO Change amount of messages and size
        msg = bytearray(10)
        sra = random.randint(0,99)
        dsa = random.randint(0,99)
        srp = random.randint(0,49)
        dsp = random.randint(0,49)
        msg[0] = sra
        msg[1] = dsa
        msg[2] = srp
        msg[3] = dsp

        msgArr.append(bytes(msg))

        count += 1

def sendToRouter():
    #TODO fill in method
    global msgArr
    # Form a UDP connection with the router
    for msg in msgArr:
        with socket(AF_INET, SOCK_DGRAM) as s:
            try:
                print("Sending MSG: ", msg.hex())
                s.sendto(msg, (HOST, ROUTER))
            except:
                print("Failed to connect to router")


if __name__ == "__main__":
    main()


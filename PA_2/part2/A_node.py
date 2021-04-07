# This is the node in the network that will generate 100 messages 
# containing 512 bytes of data each. Once generated, it will send 
# the packets to node B, which will be approved by the router R.
#
# Created By: Jason Crandall u0726408

from socket import *
import json
import sys
import random

# Define global variables
HOST = 'localhost'
ROUTER = 3333
msgArr = []

# Main function that generates 100 messages and sends them to the router
def main():
    print("Generating Messages to send")
    generateMessages()
    print("Sending...")
    sendToRouter()
    print("Finished sending")


# generateMessages is a function that creates a 512 byte message with
# a randomly generated header that loops 100 times and appends each message
# to a gloabal array.
def generateMessages():
    global msgArr
    count = 0
    while (count < 100):
        # Initialize 512 byte message with all 0's
        msg = bytearray(512)

        # Generate and assign header
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


# Loops through all the messages in the global message array
# and sends each one over UDP to R
def sendToRouter():
    global msgArr
    for msg in msgArr:
        with socket(AF_INET, SOCK_DGRAM) as s:
            try:
                s.sendto(msg, (HOST, ROUTER))
            except:
                print("Failed to send message to router")


if __name__ == "__main__":
    main()


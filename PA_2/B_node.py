# This is the node that will receive the filtered data and print the
# received header of each message.
#
# Created By: Jason Crandall u0726408

from socket import *
import json
import sys
import threading

HOST = 'localhost'
PORT = 5555

def main():
    t = threading.Thread(target = startServer, daemon=True)
    t.start()

    # Initiate the client loop for a safe exit
    while True:
        cmdInput = input("")
        if cmdInput == "q":
            exit()

def startServer():
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        while True:
            data, addr = s.recvfrom(512)
            print('Received Data: ', data.hex())

if __name__ == "__main__":
    main()
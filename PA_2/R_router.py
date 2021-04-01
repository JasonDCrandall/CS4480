# This is the router node of the assignment that will determine which data
# to forward or drop based on the data it received from the server C. It will
# then print the data for user readability.
#
# Created By: Jason Crandall u0726408

from socket import *
import json
import sys

HOST = 'localhost'
PORT = 3333
SERVER_PORT = 2222
ANODE = 4444
BNODE = 5555


def main():
    # TODO fill in the method
    # Ask for the flow table from C
    # Open a connection to A and wait for input
    # Gather all of the messages into a global array
    # for each message, match against the flow table and perform proper action
    # Modify array with new data
    # Send appropriate messages to B
    return


'''
with socket(AF_INET, SOCK_STREAM) as s:
    try:
        s.connect((HOST, SERVER_PORT))
    except:
        print(f"Server failed to respond.")
    command = {
        "command": "requestTable"
    }
    print('Sending Command: ', command)
    s.send(json.dumps(command).encode())
    data = s.recv(1024)
    print('Received Data: ', data)
'''

if __name__ == "__main__":
    main()

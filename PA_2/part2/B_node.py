# This is the node that will receive the filtered data and print the
# header of the first modified message from R
#
# Created By: Jason Crandall u0726408

from socket import *
import json
import sys
import threading

# Define global variables
HOST = 'localhost'
PORT = 5555
msgCount = 0

# Main function that initializes B as a server listening for messages
# from the Router. Prints the total messages received once complete.
def main():
    startServer()
    print("Messages Received: ", msgCount)


# startServer is a function that opens a UDP connection waiting for input.
# Once a connection is made, it will read the data and print the header if 
# it is the first modified message, otherwise it will increase the total message
# count.
def startServer():
    print("Listening for messages")
    global msgCount
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        # Listen for incoming messages
        while True:
            data, addr = s.recvfrom(2048)
            command = ''

            # Ensure the correct format is received
            try:
                jsonData = json.loads(data.decode())
                command = jsonData["command"]
            except:
                print("Unaccepted Format")

            # Close the connection once the router informs it to
            if(command == "terminate"):
                return

            # Get message from the router/parse header
            elif(command == "sendMessage"):
                message = jsonData["message"]
                sra = int(message[0:2], 16)
                dsa = int(message[2:4], 16)
                srp = int(message[4:6], 16)
                dsp = int(message[6:8], 16)
                msgCount += 1

                # Print header if it is the first modified
                if (jsonData["firstModified"]):
                    print('First Modified Header: ',sra,dsa,srp,dsp)

if __name__ == "__main__":
    main()
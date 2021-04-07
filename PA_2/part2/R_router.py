# This is the router node of the assignment that will determine which data
# to forward or drop based on the data it received from the server C. It will
# then print the data for user readability.
#
# Created By: Jason Crandall u0726408

from socket import *
import json
import sys
import threading

# Define global variables
HOST = 'localhost'
PORT = 3333
SERVER_PORT = 2222
BNODE = 5555
flowTable = None
msgCount = 0
foundMatches = []
firstModified = False

# Main function that first retreives the flow table from C,
# then acts as a server waiting for input from A.
def main():
    getFlowTable()
    startServer()


# Function that opens a TCP connection to C and requests the flow table.
# Once received, it assigns the table to the global flowTable variable.
def getFlowTable():
    global flowTable
    with socket(AF_INET, SOCK_STREAM) as s:
        # Attemp to connect to C
        try:
            s.connect((HOST, SERVER_PORT))
        except:
            print("Failed to connect to server")
            exit()

        # Build and send request
        command = {
            "command": "requestTable"
        }
        print("Requesting table")
        s.send(json.dumps(command).encode())
        data = s.recv(1024)
        print("Received flow table\n")
        flowTable = json.loads(data)


# Function that begins the server code for the Router.
# Opens a UDP connection and waits for input, and once
# input is received, it will then match that input against
# the global flow table. After it receives 100 messages, the
# connection is closed.
def startServer():
    global msgCount
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        while True:
            # Read data and match agaisnt flow table
            data, addr = s.recvfrom(2048)
            performAction(data)
            msgCount += 1

            # Terminate connection after 100 messages
            if msgCount == 100:
                print(json.dumps(flowTable, indent=4))
                terminateConnection()
                return


# The performAction function takes in a byte message, parses the header,
# then matches the header agains the global flow table. Based on the match,
# it will then perform the action found in the flow table for that message.
def performAction(data):
    global flowTable
    global firstModified

    # Convert to hex and parse header
    hexdata = data.hex()
    sra = int(hexdata[0:2], 16)
    dsa = int(hexdata[2:4], 16)
    srp = int(hexdata[4:6], 16)
    dsp = int(hexdata[6:8], 16)

    # Iterate through flow table to find a match
    for entry in flowTable["table"]:
        match = entry["match"]
        action = entry["action"]
        statistics = entry["statistics"]

        if(eval(match)):
            # Print if it is the first match found
            if(match not in foundMatches):
                foundMatches.append(match)
                print(f"First Match For: {match}\nMessage Header: {sra} {dsa} {srp} {dsp}\n")

            entry["statistics"] = statistics + 1

            # Forward packet if matches action
            if(action == "forward"):
                forwardPacket(data, False)

            # If action is modify, change the header to the flow table's values
            elif (action != "drop"):
                # Modify header
                ldict = {}
                exec(action, globals(),ldict)
                sra = ldict['sra']
                srp = ldict['srp']

                # Reformat messsage
                updatedMsg = bytearray.fromhex(hexdata)
                updatedMsg[0] = sra
                updatedMsg[2] = srp
                packet = bytes(updatedMsg)

                # Inform B to print new header if it is the first changed header
                if(not firstModified):
                    firstModified = True
                    forwardPacket(packet, firstModified)
                else:
                    forwardPacket(packet,False)
            break


# forwardPacket is a function that takes in a byte packet, and a boolean value
# determining if the header of the packet has been modified or not. It builds
# a command to send to B consisting of the message contents, as well as whether
# or not it is the first changed header to be printed.
def forwardPacket(packet, modified):
    # Build command
    command = {
        "command": "sendMessage",
        "message": packet.hex(),
        "firstModified": modified
    }
    # Send command
    with socket(AF_INET, SOCK_DGRAM) as s:
        try:
            s.sendto(json.dumps(command).encode(), (HOST, BNODE))
        except:
            print("Failed to connect to B Node")
    return


# terminateConnection is a function that builds a command informing B
# that it should cease listening for further messages.
def terminateConnection():
    # Build command
    command = {
        "command": "terminate"
    }
    # Send command
    with socket(AF_INET, SOCK_DGRAM) as s:
        try:
            s.sendto(json.dumps(command).encode(), (HOST, BNODE))
        except:
            print("Failed to connect to B Node")


if __name__ == "__main__":
    main()

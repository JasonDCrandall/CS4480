# This is the router node of the assignment that will determine which data
# to forward or drop based on the data it received from the server C. It will
# then print the data for user readability.
#
# Created By: Jason Crandall u0726408

from socket import *
import json
import sys
import threading

HOST = 'localhost'
PORT = 3333
SERVER_PORT = 2222
ANODE = 4444
BNODE = 5555
flowTable = None
msgCount = 0
foundMatches = []
firstModified = False


def main():
    # Ask for the flow table from C
    getFlowTable()
    # Open a connection to A and wait for input
    startServer()


def getFlowTable():
    global flowTable
    with socket(AF_INET, SOCK_STREAM) as s:
        try:
            s.connect((HOST, SERVER_PORT))
        except:
            print("Failed to connect to server")
            exit()
        command = {
            "command": "requestTable"
        }
        print("Requesting table")
        s.send(json.dumps(command).encode())
        data = s.recv(1024)
        print("Received flow table\n")
        flowTable = json.loads(data)

def startServer():
    global msgCount
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        while True:
            data, addr = s.recvfrom(2048)
            #print(f"Received msg from {addr}: {data}")
            performAction(data)
            msgCount += 1
            if msgCount == 100:
                print(json.dumps(flowTable, indent=4))
                terminateConnection()
                return

def performAction(data):
    global flowTable
    global firstModified
    hexdata = data.hex()
    sra = int(hexdata[0:2], 16)
    dsa = int(hexdata[2:4], 16)
    srp = int(hexdata[4:6], 16)
    dsp = int(hexdata[6:8], 16)

    #print("Header data at R: ", sra, dsa, srp, dsp)
    for entry in flowTable["table"]:
        match = entry["match"]
        action = entry["action"]
        statistics = entry["statistics"]
        if(eval(match)):
            if(match not in foundMatches):
                foundMatches.append(match)
                print(f"First Match For: {match}\nMessage Header: {sra} {dsa} {srp} {dsp}\n")
            entry["statistics"] = statistics + 1
            if(action == "forward"):
                forwardPacket(data, False)
            elif (action != "drop"):
                ldict = {}
                exec(action, globals(),ldict)
                sra = ldict['sra']
                srp = ldict['srp']
                # Reformat header
                updatedMsg = bytearray.fromhex(hexdata)
                updatedMsg[0] = sra
                updatedMsg[2] = srp
                packet = bytes(updatedMsg)
                if(not firstModified):
                    firstModified = True
                    forwardPacket(packet, firstModified)
                else:
                    forwardPacket(packet,False)
            break

def forwardPacket(packet, modified):
    command = {
        "command": "sendMessage",
        "message": packet.hex(),
        "firstModified": modified
    }
    with socket(AF_INET, SOCK_DGRAM) as s:
        try:
            # print("Sending MSG: ", packet.hex())
            s.sendto(json.dumps(command).encode(), (HOST, BNODE))
        except:
            print("Failed to connect to B Node")
    return

def terminateConnection():
    command = {
        "command": "terminate"
    }
    with socket(AF_INET, SOCK_DGRAM) as s:
        try:
            # print("Sending MSG: ", packet.hex())
            s.sendto(json.dumps(command).encode(), (HOST, BNODE))
        except:
            print("Failed to connect to B Node")


if __name__ == "__main__":
    main()

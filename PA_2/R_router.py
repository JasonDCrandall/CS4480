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


def main():
    # TODO fill in the method
    # Ask for the flow table from C
    getFlowTable()
    print("Initial Table from C: ",flowTable)
    # Open a connection to A and wait for input
    t = threading.Thread(target = startServer, daemon=True)
    t.start()

    # Initiate the client loop for a safe exit
    while True:
        cmdInput = input("")
        if cmdInput == "q":
            exit()
    # Gather all of the messages into a global array
    # for each message, match against the flow table and perform proper action
    # Modify array with new data
    # Send appropriate messages to B
    return


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
        print("Sending Command: ", command)
        s.send(json.dumps(command).encode())
        data = s.recv(1024)
        flowTable = json.loads(data)

def startServer():
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        while True:
            data, addr = s.recvfrom(1024)
            print(f"Received msg from {addr}: {data}")
            performAction(data)
            # t = threading.Thread(target = performAction, daemon=True, args=(data,))
            # t.start()

def performAction(data):
    global flowTable
    hexdata = data.hex()
    print(hexdata)
    sra = int(hexdata[0:2], 16)
    dsa = int(hexdata[2:4], 16)
    srp = int(hexdata[4:6], 16)
    dsp = int(hexdata[6:8], 16)

    print("Header data at R: ", sra, dsa, srp, dsp)
    for entry in flowTable["table"]:
        match = entry["match"]
        action = entry["action"]
        statistics = entry["statistics"]
        if(eval(match)):
            print("Match on: ", match)
            entry["statistics"] = statistics + 1
            if(action == "forward"):
                forwardPacket()
            elif (action != "drop"):
                exec(action)
                # Reformat header
                forwardPacket()
            break

def forwardPacket():

    return


if __name__ == "__main__":
    main()

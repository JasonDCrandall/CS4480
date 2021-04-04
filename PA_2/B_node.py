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
msgCount = 0

def main():
    startServer()
    print(msgCount)
    # t = threading.Thread(target = startServer, daemon=True)
    # t.start()

    # # Initiate the client loop for a safe exit
    # while True:
    #     cmdInput = input("")
    #     if cmdInput == "q":
    #         exit()

def startServer():
    global msgCount
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        while True:
            data, addr = s.recvfrom(2048)
            command = ''
            try:
                jsonData = json.loads(data.decode())
                command = jsonData["command"]
            except:
                print("Unaccepted Format")
            if(command == "terminate"):
                return
            elif(command == "sendMessage"):
                message = jsonData["message"]
                sra = int(message[0:2], 16)
                dsa = int(message[2:4], 16)
                srp = int(message[4:6], 16)
                dsp = int(message[6:8], 16)
                msgCount += 1
                if (jsonData["firstModified"]):
                    print('First Modified Header: ',sra,dsa,srp,dsp)

if __name__ == "__main__":
    main()
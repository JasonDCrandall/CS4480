# This acts as the C server that contains the routing table information for the rest of
# the program to function properly. No loop is required as once it is sent to the R router,
# the connection will be terminated.
#
# Created By: Jason Crandall u0726408

from socket import *
import json
import sys

HOST = 'localhost'
PORT = 2222
ROUTER = 3333

flowTable = {
    "table": [
        {
            "match": "sra <= 20 and dsa <= 20 and srp > 10 and dsp > 10",
            "action": "sra = 21;srp = 41",
            "statistics": 0
        },
        {
            "match": "sra > 40 and dsa > 40 and srp > 10 and dsp > 10",
            "action": "forward",
            "statistics": 0
        },
        {
            "match": "srp <= 10 or dsp <= 10",
            "action": "drop",
            "statistics": 0
        },
        {
            "match": "'No Match Found'",
            "action": "drop",
            "statistics": 0
        }
    ]
}

def main():
    # Open a connection and wait for input from the router
    with socket(AF_INET,SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(2)
        connection, addr = s.accept()
        with connection:
            print("Connected by ", addr)
            data = connection.recv(1024)
            print("Received Data: ", data.decode())
            command = ''
            try:
                jsonData = json.loads(data.decode())
                command = jsonData['command']
            except:
                error = "Unrecognized Format"
                connection.send(error.encode())
            if(command == "requestTable"):
                tableData = json.dumps(flowTable)
                print("Sending flow table")
                connection.send(tableData.encode())

if __name__ == "__main__":
    main()
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

with socket(AF_INET, SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(2)
    connection, addr = s.accept()
    with connection:
        print('Connected by', addr)
        data = connection.recv(1024)
        print("Received data: ", data)
        command = ''
        try:
            jsonData = json.loads(data.decode())
            command = jsonData['command']
        except:
            returnMessage = "Unaccepted Format"
            connection.send(returnMessage.encode())
        returnMessage = "Got the message"
        connection.send(returnMessage.encode())

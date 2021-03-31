#!/usr/bin/python3
'''
p2p.py is a peer to peer networking program that allows the transfer of files accross 3 nodes.
The nodes can be joined one at a time, but once online must stay online to maintain functionality.

Created by: Jason Crandall
uID: u0726408
'''
from socket import *
import json
from node import Node
import sys
import threading

# Declaration of global varialbes and instantiating the set ports for each of the nodes
HOST = 'localhost'
nodeList = [Node(0, 8888), Node(1, 7777), Node(2, 6666)]
myNode = None
leaderID = None

# Main function: acts as the client in the program which continuously asks
# the user for input. Based on that input, the client will send out
# the corresponding command via json data out to the current node that 
# is set as the leader.
def main():
    startup()
    electLeader()
    print("Leader ID: ", leaderID)
    if myNode.nodeID != leaderID:
        submitFileList(nodeList[leaderID])

    # Start the server on a separate thread to allow concurrency
    t = threading.Thread(target = startServer, daemon=True)
    t.start()

    # Initiate the client loop
    while True:
        cmdInput = input("Enter a command\nQuit: q\nShow known files: files\nRequest a file: getFile <filename>\n")
        if cmdInput == "q":
            exit()
        if cmdInput == "files":
            for node in nodeList:
                print("Node: ",node.nodeID)
                print(node.fileList)
        if cmdInput.startswith("getFile"):
            files = cmdInput.split(" ")
            fileLocation = getFileLocation(files[1])
            if fileLocation["returnType"] == "fileLocationError":
                print(fileLocation["error"])
            elif fileLocation["returnType"] == "fileLocation":
                getFile(fileLocation)

# Startup: initializes the current node based on the command line inputs by the user.
# Sets the node ID, the files this node is willing to share, and defaults the leader node to this node
def startup():
    global myNode
    global leaderID
    nodeID = int(sys.argv[1])

    # Remove the first two args from the cmd line input for the full file list
    files = sys.argv
    files.pop(0)
    files.pop(0)

    # Check each file the node is willing to share to verify it exists
    for file in files:
        try:
            f = open(file, "r")
        except:
            print(f"The file '{file}' was not found.")
            exit()
        f.close()

    # Verify it is a valid node ID
    if nodeID > len(nodeList):
        exit()  
    
    myNode = nodeList[nodeID]
    myNode.fileList = files
    print("My port is: ", myNode.port)
    print("My nodeID is: ",myNode.nodeID)
    print("My files are: ", files)
    leaderID = myNode.nodeID

# StartServer: Initializes the server loop that will be waiting for new connections.
# Based on the json data received, the server will respond with the appropriate data/action
# in json format as well
def startServer():
    global myNode
    global leaderID
    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind((HOST, myNode.port))
        s.listen(2)
        # Wait for new connections
        while True:
            connection, addr = s.accept()
            with connection:
                print('Connected by', addr)
                data = connection.recv(1024)
                print("Received data: ", data)
                command = ''
                
                # Make sure the data from the client is in the proper format
                try:
                    jsonData = json.loads(data.decode())
                    command = jsonData['command']
                except:
                    returnMessage = "Unaccepted Format"
                    connection.send(returnMessage.encode())

                # Parse and execute the command received from the clients

                # Send the file data directly if asking for a valid file
                if command == "getFile":
                    filename = jsonData["filename"]
                    file = open(filename, 'rb')
                    file_data = file.read(1024)
                    print("Sending Response: ", file_data)
                    connection.send(file_data)

                # If the electLeader command is called, it will calculate the proper leader node
                # If the sender is the leader, this will return the files it is willing to share
                elif command == "electLeader":
                    nodeId = int(jsonData["myID"])
                    fileList = []
                    if nodeId < leaderID:
                        leaderID = nodeId
                        fileList = myNode.fileList
                        for node in nodeList:
                            if node.nodeID != myNode.nodeID and node.nodeID != leaderID:
                                nodeList[node.nodeID].fileList = []
                    else:
                        fileList = [] #Stay empty
                    returnMessage = {
                        "returnType":"leaderElection",
                        "id": leaderID,
                        "fileList": fileList
                    }
                    print("Sending Response: ", returnMessage)
                    print("Leader ID: ", str(leaderID))
                    connection.send(json.dumps(returnMessage).encode())

                # If receives the submitFileList command, it simply responds with an OK code
                elif command == "submitFileList":
                    files = jsonData["list"]
                    nodeId = jsonData["id"]
                    nodeList[nodeId].fileList = files
                    returnMessage = {
                        "returnType":"fileList",
                        "response":"OK"
                    }
                    print("Sending Response: ", returnMessage)
                    connection.send(json.dumps(returnMessage).encode())

                # If asked for the file location, it checks where the file is located, then 
                # responds with a "File Not Found" if it doesn't exist, or with the node
                # details (ip, port, filename) if it is a known file
                elif command == "getFileLocation":
                    filename = jsonData["filename"]
                    returnMessage = None
                    for node in nodeList:
                        if filename in node.fileList:
                            returnMessage = {
                                "returnType": "fileLocation",
                                "address": HOST,
                                "filename": filename,
                                "port": node.port
                            }
                            break
                        else:
                            returnMessage = {
                                "returnType": "fileLocationError",
                                "error": "File Not Found"
                            }
                    print("Sending Response: ", returnMessage)
                    connection.send(json.dumps(returnMessage).encode())
            print("Enter a command\nQuit: q\nShow known files: files\nRequest a file: getFile <filename>\n")

# Elect leader will reach out to each of nodes found in the nodeList, sends it's node id.
# Once it retrieves the data from the server, it will update the nodelist and keep track of
# the current leader node
def electLeader():
    global myNode
    global leaderID
    for node in nodeList:
        if node.nodeID == myNode.nodeID:
            continue
        with socket(AF_INET, SOCK_STREAM) as s:
            try:
                s.connect((HOST, node.port))
            except:
                print(f"Node {node.nodeID} failed to respond.")
                continue
            command = {
                "command":"electLeader",
                "myID": myNode.nodeID
            }
            print('Sending Command: ',command)
            s.send(json.dumps(command).encode())
            data = s.recv(1024)
            print('Received Data: ', data)
            try:
                jsonData = json.loads(data.decode())
            except:
                print(f"Node {node.nodeID} gave an invalid response.")
                continue
            if jsonData["returnType"] == 'leaderElection':
                returnedID = int(jsonData["id"])
                node.fileList = jsonData["fileList"]
                leaderID = returnedID

# SubmitFile List will connect to the current leader node and provide
# the list of files it is willing to share on the network
def submitFileList(node):
    with socket(AF_INET, SOCK_STREAM) as s:
        try:
            s.connect((HOST, node.port))
        except:
            print(f"Node {node.nodeID} failed to respond.")
            return
        command = {
            "command":"submitFileList",
            "id": myNode.nodeID,
            "list": myNode.fileList
        }
        print('Sending Command: ',command)
        s.send(json.dumps(command).encode())
        data = s.recv(1024)
        print("Received Data: ", data.decode())

# GetFileLocation connects to the current leader node and sends the command to get a location.
# Returns: the json data that the server sends back
def getFileLocation(file):
    leader = nodeList[leaderID]
    locationData = None
    with socket(AF_INET,SOCK_STREAM) as s:
        try:
            s.connect((HOST, leader.port))
        except:
            print(f"Node {leader.nodeID} failed to respond.")
            return None
        command = {
            "command": "getFileLocation",
            "filename": file
        }
        print('Sending Command: ',command)
        s.send(json.dumps(command).encode())
        data = s.recv(1024)
        print("Received Data: ", data.decode())
        locationData = json.loads(data.decode())
    return locationData

# GetFile takes in the json data of a 'getFileLocation' response and parses out the node data.
# Using that data, it will connect to that node, request the file information, and download the file locally
def getFile(fileLocation):
    fileAddr = fileLocation["address"]
    filePort = fileLocation["port"]
    filename = fileLocation["filename"]
    with socket(AF_INET,SOCK_STREAM) as s:
        try:
            s.connect((fileAddr,filePort))
        except:
            print(f"Node failed to respond")
            return
        command = {
            "command": "getFile",
            "filename": filename
        }
        print("Sending Command: ", command)
        s.send(json.dumps(command).encode())
        data = s.recv(1024)
        print("Received Data: ", data.decode())
        file = open(filename, 'wb')
        file.write(data)
        file.close()


        

if __name__ == "__main__":
    main()

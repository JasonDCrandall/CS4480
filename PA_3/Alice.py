# Code representing alice in the secure text transfer
from socket import *
import json

HOST = "localhost"
BPORT = 3344
APORT = 4455
# Below are the steps needed from Alice's side of the program:

# Request and verify Bob's public Key
def requestBobsKey():
    with socket(AF_INET, SOCK_STREAM) as s:
        try:
            s.connect((HOST, BPORT))
        except:
            print(f"Bob failed to respond.")
            return
        command = {
            "command":"requestKey"
        }
        print('Sending Command: ',command)
        s.send(json.dumps(command).encode())
        data = s.recv(1024)
        print('Received Data: ', data)
        try:
            jsonData = json.loads(data.decode())
        except:
            print(f"Bob gave an invalid response.")
        # if jsonData["returnType"] == 'leaderElection':
        #     returnedID = int(jsonData["id"])
        #     node.fileList = jsonData["fileList"]
        #     leaderID = returnedID
# Use crypto lib for integrity, encryption, and signing of a msg to send to bob

# Transfer message with symmetric key

# End


if __name__ == "__main__":
    main()
'''
The Node class is a representation of each of the properties found on the individual
nodes in the Peer to Peer network
'''
import random

class Node:
    nodeID = 0
    port = 8888
    isLeader = False
    fileList = []

    def __init__(self, nodeID, port):
        self.nodeID = nodeID
        self.port = port

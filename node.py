import chord
import socket
import hashlib
import utils
import grpc
import chord_pb2_grpc
import chord_pb2
from concurrent import futures

class Node():
    def __init__(self, ring_bits):
        self.ip = socket.gethostbyname(socket.gethostname()).encode('utf-8') # IP Address of node as bytes
        self.ring_bits = ring_bits # No. of bits in identifier circle
        self.id = int(hashlib.sha1(self.ip).hexdigest(), 16) % (2**ring_bits) # ID of node

        self.successor = None # Successor (list?) in (ID, IP addr) format
        self.predecessor = None # Predecessor in (ID, IP addr) format
        
        # Finger Table of size `ring_bits` in (ID, IP addr format)
        self.ftable = None

    #Set successor and predecssor of a node
    def set_predecessor(self, id, ip_addr):
        self.predecessor = (id, ip_addr)

    def set_successor(self, id, ip_addr):
        self.successor = (id, ip_addr)
    
    '''
    Given a key k, find the node responsible for k
    '''
    def findSuccessor(k):
        if k > self.id and k <= self.successor[0]:
            return self.successor
        
    '''
    Search the Finger Table for the highest predecessor of k
    Returns node in (ID, IP Addr) format
    '''
    def closestPrecedingNode(self, k):
        #TODO : k must not be equal to self.id!
        target_distance = utils.circular_distance(self.id, k, self.ring_bits)

        for i in range(self.ring_bits - 1, -1, -1):
            ith_finger = self.ftable[i]
            if ith_finger is None:
                continue

            ith_finger_distance = utils.circular_distance(self.id, ith_finger[0], self.ring_bits)
            if ith_finger_distance > 0 and ith_finger_distance < target_distance:
                return self.ftable[i]
        
        return (self.id, self.ip)

    def serve(self):
        ip = '[::]:50051'
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        node = Node(ring_bits = 128)
        chord_pb2_grpc.add_ChordServiceServicer_to_server(
            chord.ChordServicer(node), server)
        server.add_insecure_port(ip)
        server.start()

        print(f'[chord] Listening on {ip}')
        server.wait_for_termination()
    
    def printIP(self):
        print(f'Node IP = {self.ip}')
        print(f'Node ID = {self.id}')

def test_closestPrecedingNode():
    node = Node(ring_bits = 6)
    node.id = 8
    node.ftable = [ (14, '192.168.0.1'),
                        (14, '192.168.0.1'),
                        (14, '192.168.0.1'),
                        (21, '192.168.0.2'),
                        (32, '192.168.0.3'),
                        (42, '192.168.0.4')]
    for i in range(0, 2**node.ring_bits):
        print(f'Key = {i}, Closest Preceding = {node.closestPrecedingNode(i)}')

def main():
    node = Node(ring_bits = 128)
    node.printIP()
    node.serve()

if __name__ == "__main__":
    main()
    
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
        self.ip = socket.gethostbyname(socket.gethostname()) # IP Address of node as str
        self.ip_bytes = self.ip.encode('utf-8') # IP Address of node as bytes
        self.ring_bits = ring_bits # No. of bits in identifier circle
        self.id = int(hashlib.sha1(self.ip_bytes).hexdigest(), 16) % (2**ring_bits) # ID of node

        self.successor = None # Successor (list?) in (ID, IP addr) format
        self.predecessor = None # Predecessor in (ID, IP addr) format
        
        # Finger Table of size `ring_bits` in (ID, IP addr format)
        self.ftable = [None] * ring_bits

        # Bootstrapper info
        self.bootstrapper_ip = 'c220g1-031107.wisc.cloudlab.us:50051'

    '''
    Clears the bootstrapper's node table
    ONLY FOR DEBUGGING!!!!!!!!!
    '''
    def clearBootstrapper(self):
        channel = grpc.insecure_channel(self.bootstrapper_ip)
        stub = chord_pb2_grpc.BootstrapServiceStub(channel)
        request = chord_pb2.Empty()

        response = stub.clearTable(request)

        print('[chord] clearBootstrapper')

    '''
    Contact the bootstrapper server and get the (ID, IP) of an existing
    node in the Chord ring
    '''
    def contactBootstrapper(self):
        channel = grpc.insecure_channel(self.bootstrapper_ip)
        stub = chord_pb2_grpc.BootstrapServiceStub(channel)
        request = chord_pb2.Empty()

        response = stub.getNode(request)
        print(f'[chord] contactBootstrapper returned ({response.id}, {response.ip})')
        return (response.id, response.ip)

    def addToBootstrapper(self):
        print('[chord] Adding self to Bootstrapper..')
        channel = grpc.insecure_channel(self.bootstrapper_ip)
        stub = chord_pb2_grpc.BootstrapServiceStub(channel)
        request = chord_pb2.NodeInfo(id = self.id, ip = self.ip)
        stub.addNode(request)

    '''
    Join the existing chord ring OR become the first node
    '''
    def join(self):
        n_dash = self.contactBootstrapper() # Find existing node in ring

        if n_dash.id == -1:
            self.predecessor = None
            self.successor = (self.id, self.ip)
            # TODO: Add ourself to the Bootstrapper's table only after keys are transferred + pointers are set
            self.addToBootstrapper()
            return

        # successor = n'.find successor(n)
        target_ip = n_dash[1]
        is_final = False
        while not is_final:
            channel = grpc.insecure_channel(target_ip)
            stub = chord_pb2_grpc.ChordServiceStub(channel)
            request = chord_pb2.FindSuccessorRequest(id = self.id)
            response = stub.findSuccessor(request)
            target_ip = response.ip
            is_final = response.is_final

        self.set_successor(response.id, response.ip)

    #Set successor and predecssor of a node
    def set_predecessor(self, id, ip_addr):
        self.predecessor = (id, ip_addr)

    def set_successor(self, id, ip_addr):
        self.successor = (id, ip_addr)
        self.ftable[0] = self.successor
    
    '''
    Given a key k, find the node responsible for k
    Working diagram -
    <node> <---------> Node A
    <node> <---------> Node B ... (no RPC chaining)
    '''
    def findSuccessor(self, k):
        # channel = grpc.insecure_channel(n_dash[1])
        # stub = chord_pb2_grpc.ChordServiceStub(channel)
        # request = chord_pb2.FindSuccessorRequest(id = self.id)
        # response = stub.findSuccessor(request)

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
    #node.contactBootstrapper()
    #node.serve()

if __name__ == "__main__":
    main()
    
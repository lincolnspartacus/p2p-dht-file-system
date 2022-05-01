import chord
import socket
import hashlib
import utils
import grpc
import sys
import chord_pb2_grpc
import chord_pb2
from stabilize import Stabilize
from concurrent import futures

class Node():
    def __init__(self, ring_bits):
        #self.ip = socket.gethostbyname(socket.gethostname()) + ':' + sys.argv[1] # ':50051' # IP Address of node as str
        self.ip = '0.0.0.0:' + sys.argv[1]
        self.ip_bytes = self.ip.encode('utf-8') # IP Address of node as bytes
        self.ring_bits = ring_bits # No. of bits in identifier circle
        self.id = int(hashlib.sha1(self.ip_bytes).hexdigest(), 16) % (2**ring_bits) # ID of node

        self.successor = (-1, 'null') # Successor (list?) in (ID, IP addr) format
        self.predecessor = (-1, 'null') # Predecessor in (ID, IP addr) format
        
        # Finger Table of size `ring_bits` in (ID, IP addr format)
        self.ftable = [(-1, 'null')] * ring_bits

        #Utility threads
        self.stabilize = Stabilize(self)

        # Bootstrapper info
        #self.bootstrapper_ip = 'c220g1-031107.wisc.cloudlab.us:50051'
        self.bootstrapper_ip = 'localhost:40051'


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
        # TODO : What if the returned n' is actually this node itself?? BOOM!

        if n_dash[0] == -1:
            self.predecessor = (-1, 'null')
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
        # TODO: Add ourself to the Bootstrapper's table only after keys are transferred + pointers are set
        self.addToBootstrapper()

    #Set successor and predecssor of a node
    def set_predecessor(self, id, ip_addr):
        self.predecessor = (id, ip_addr)

    def set_successor(self, id, ip_addr):
        self.successor = (id, ip_addr)
        self.ftable[0] = self.successor

    def delete_successor(self):
        # delete the successor from finger table and fill in with the most recent successor after that
        print('*****NOW DELETE SUCCESSOR*****')
        if self.successor == -1:
            return -1

        next_suc = None
        suc_id = self.successor[0]
        # find the closest successor
        for i in range(0, self.ring_bits):
            suc_info = self.ftable[i] #(id, ip)
            if suc_info[0] != -1 and suc_info[0] != suc_id:
                next_suc = suc_info
                break

        # for loop needed because Finger table can be and we need update only "N14" entries
        # N8 + 1 -> N14 
        # N8 + 2 -> N14 
        # N8 + 4 -> N14 
        # N8 + 8 -> N21
        for i in range(0, self.ring_bits):
            # ftable structure: [(id, ip), (id, ip)]
            if self.ftable[i][0] == suc_id:
                # replace this successor with next possible successor, otherwise to set it to be (-1, null)
                if next_suc is not None:
                    self.ftable[i] = next_suc
                else:
                    self.ftable[i] = (-1, 'null')
            else:
                break

        self.set_successor(self.ftable[0][0], self.ftable[0][1])
        print('[delete_successor] - {} finger table is {}'.format(self.id, self.ftable))
        return 0
    
    # used to contact successor and notify the existence of current node
    def notify_successor(self):
        if self.successor[0] == -1 or self.successor[0] == self.id:
            return

        print('[notify_successor] successorId:{}  |  succesorAddr:{}'.format(self.successor[0], self.successor[1]))

        channel = grpc.insecure_channel(self.successor[1])
        stub = chord_pb2_grpc.ChordServiceStub(channel)
        notify_req = chord_pb2.NotifyRequest(predecessorId=self.id, addr=self.ip)
        try:
                stub.notify(notify_req, timeout=20)
        except Exception as e:
            print(str(e))
            print("[notify_successor] Node#{} rpc error when notify to {}".format(self.id, self.successor[0]))

    #Check if predecessor is alive else set it to null
    def check_predecessor(self):
        if self.predecessor[0] == -1:
            return
        channel = grpc.insecure_channel(self.predecessor[1])
        stub = chord_pb2_grpc.ChordServiceStub(channel)
        check_predecessor_request = chord_pb2.Empty()
        try:
            stub.checkPredecessor(check_predecessor_request, timeout=20)
        except:
            print("[check_predecessor] Node#{} rpc error when to {}".format(self.id, self.predecessor[0]))
            self.predecessor = (-1, "null")

    def update_kth_finger_table_entry(self, k, successor_id, successor_addr):
        # print('*****NOW UPDATE FINGER ENTRY*****')
        self.ftable[k] = (successor_id, successor_addr)
        if k == 0:
           self.set_successor(successor_id, successor_addr)
        # print('node {} updated finger table is: {}'.format(self.id, str(self.finger_table)))

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
            if ith_finger[0] == -1:
                continue

            ith_finger_distance = utils.circular_distance(self.id, ith_finger[0], self.ring_bits)
            if ith_finger_distance > 0 and ith_finger_distance < target_distance:
                return self.ftable[i]
        
        return (self.id, self.ip)

    def get_successors_predecessor(self):
        if self.successor[0] == -1:
            return (-1,"null")
        if self.successor[0] == self.id and self.predecessor[0] == -1:
            return (self.id, self.ip)
        if self.successor[0] == self.id and self.predecessor[0] != -1:
            print("Updating successor")
            self.set_successor(self.predecessor[0],self.predecessor[1])
            return (self.id, self.ip)
        channel = grpc.insecure_channel(self.successor[1])
        stub = chord_pb2_grpc.ChordServiceStub(channel)
        request = chord_pb2.Empty()
        response = stub.findSuccessorsPred(request)
        return (response.id,response.ip)

    def serve(self):
        ip = '0.0.0.0:' + sys.argv[1]
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        chord_pb2_grpc.add_ChordServiceServicer_to_server(
            chord.ChordServicer(self), server)
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
    print("port number: " + sys.argv[1]);
    node = Node(ring_bits = 16)
    node.printIP()
    #node.contactBootstrapper()
    node.join()
    node.stabilize.start()
    node.serve()

if __name__ == "__main__":
    main()
    
import chord
import socket
import threading
import hashlib
import utils
import grpc
import sys
import chord_pb2_grpc
import chord_pb2
from stabilize import Stabilize
from fix_finger import FixFinger
from concurrent import futures
from chord_replicate import ReplicateThread
import os
import pickle as pkl

class Node():
    def __init__(self, ring_bits):
        #self.ip = socket.gethostbyname(socket.gethostname()) + ':' + sys.argv[1] # ':50051' # IP Address of node as str
        self.ip = '0.0.0.0:' + sys.argv[1]
        self.ip_bytes = self.ip.encode('utf-8') # IP Address of node as bytes
        self.ring_bits = ring_bits # No. of bits in identifier circle
        self.id = int(hashlib.sha1(self.ip_bytes).hexdigest(), 16) % (2**ring_bits) # ID of node

        self.successor = (-1, 'null') # Successor (list?) in (ID, IP addr) format
        self.predecessor = (-1, 'null') # Predecessor in (ID, IP addr) format
        self.successor_list_len = 2 #Max successor list length
        self.successor_list = [(-1,'null')] * self.successor_list_len
        
        # Finger Table of size `ring_bits` in (ID, IP addr format)
        self.ftable = [(self.id, self.ip)] * ring_bits

        #Utility threads
        self.stabilize = Stabilize(self)
        self.fix_finger = FixFinger(self)

        # Locks
        self.successor_lock = threading.Lock()
        self.predecessor_lock = threading.Lock()
        self.replicated_lock = threading.Lock()
        self.owner_lock = threading.Lock()

        # Data structures to track files on this node
        # {public_key+filname : (fileid, checksum)}
        self.owner_dict = {}
        self.replicated_dict = {}

        # Bootstrapper info
        #self.bootstrapper_ip = 'c220g1-031107.wisc.cloudlab.us:50051'
        self.bootstrapper_ip = 'localhost:40051'

        self.storage_dir = str(self.id)+'/'
        if not os.path.isdir(self.storage_dir):
            os.mkdir(self.storage_dir)
        
        self.owner_filepath = os.path.join(self.storage_dir, '.owner')
        self.replicated_filepath = os.path.join(self.storage_dir, '.replicated')
        if os.path.exists(self.owner_filepath):
            with open(self.owner_filepath, 'rb') as f:
                self.owner_dict = pkl.load(f)
        if os.path.exists(self.replicated_filepath):
            with open(self.replicated_filepath, 'rb') as f:
                self.replicated_dict = pkl.load(f)


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
    Find the current successor for the given chord identifier
    Request is routed and the chord ring is traversed starting from target_ip 
    '''
    def find_successor(self, target_id, target_ip):
        successor = self.get_successor()
        if successor[0] == -1 or successor[0] == self.id:
            return successor
        n_succ_distance = utils.circular_distance(self.id, successor[0], self.ring_bits)
        n_target_distance = utils.circular_distance(self.id, target_id, self.ring_bits)

        if n_target_distance <= n_succ_distance:
            return successor

        try:
            # successor = n'.find successor(n)
            is_final = False
            while not is_final:
                channel = grpc.insecure_channel(target_ip)
                stub = chord_pb2_grpc.ChordServiceStub(channel)
                request = chord_pb2.FindSuccessorRequest(id = target_id)
                response = stub.findSuccessor(request)
                target_ip = response.ip
                is_final = response.is_final

            return (response.id, response.ip)
        except:
            print('[find_successor] {}: Failed target_id {} target_ip {}'.format(self.id, target_id, target_ip))
            return (self.id, self.ip)
       
    '''
    Join the existing chord ring OR become the first node
    '''
    def join(self):
        n_dash = self.contactBootstrapper() # Find existing node in ring
        # TODO : What if the returned n' is actually this node itself?? BOOM!

        if n_dash[0] == -1:
            self.set_predecessor(-1, 'null')
            self.set_successor(self.id, self.ip)
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
        self.predecessor_lock.acquire()
        self.predecessor = (id, ip_addr)
        self.predecessor_lock.release()

    def get_predecessor(self):
        self.predecessor_lock.acquire()
        ret = (self.predecessor[0], self.predecessor[1])
        self.predecessor_lock.release()
        return ret

    def get_successor(self):
        self.successor_lock.acquire()
        ret = (self.successor[0], self.successor[1])
        self.successor_lock.release()
        return ret

    def set_successor(self, id, ip_addr):
        self.successor_lock.acquire()

        print("****SET SUCCESSOR***",id)
        old_set = set(self.successor_list)
        self.successor = (id, ip_addr)
        self.ftable[0] = self.successor
        self.successor_list[0] = self.successor
        new_set = set(self.successor_list)
        if old_set != new_set:
            self.onSuccessorListChanged(old_set, new_set)

        self.successor_lock.release()

    def set_successor_list(self, new_list):
        self.successor_lock.acquire()

        self.successor_list = new_list
        self.ftable[0] = new_list[0]
        self.successor = new_list[0]

        self.successor_lock.release()

    def get_successor_list(self):
        self.successor_lock.acquire()
        ret = self.successor_list.copy()
        self.successor_lock.release()
        return ret

    # Update owner_dict and write it to disk
    def addToOwnerDict(self, publickey_filename, fileid, checksum):
        self.owner_lock.acquire()
        self.owner_dict[publickey_filename] = (fileid, checksum)
        utils.atomic_pkl_dump(self.owner_dict, self.owner_filepath)
        self.owner_lock.release()
    
    def removeFromOwnerDict(self, delete_dict):
        self.owner_lock.acquire()
        for publickey_filename in delete_dict:
            try:
                self.owner_dict.pop(publickey_filename)
            except:
                pass
        utils.atomic_pkl_dump(self.owner_dict, self.owner_filepath)
        self.owner_lock.release()

    # Update replicated_dict and write it to disk
    def addToReplicatedDict(self, publickey_filename, fileid, checksum):
        self.replicated_lock.acquire()
        self.replicated_dict[publickey_filename] = (fileid, checksum)
        utils.atomic_pkl_dump(self.replicated_dict, self.replicated_filepath)
        self.replicated_lock.release()

    
    # used to contact successor and notify the existence of current node
    def notify_successor(self):
        successor = self.get_successor()
        if successor[0] == -1 or successor[0] == self.id:
            return

        print('[notify_successor] successorId:{}  |  succesorAddr:{}'.format(successor[0], successor[1]))

        channel = grpc.insecure_channel(successor[1])
        stub = chord_pb2_grpc.ChordServiceStub(channel)
        notify_req = chord_pb2.NotifyRequest(predecessorId=self.id, addr=self.ip)
        try:
                stub.notify(notify_req, timeout=20)
        except Exception as e:
            print(str(e))
            print("[notify_successor] Node#{} rpc error when notify to {}".format(self.id, successor[0]))

    #Check if predecessor is alive else set it to null
    def check_predecessor(self):
        predecessor = self.get_predecessor()
        if predecessor[0] == -1:
            return
        channel = grpc.insecure_channel(predecessor[1])
        stub = chord_pb2_grpc.ChordServiceStub(channel)
        check_predecessor_request = chord_pb2.Empty()
        try:
            stub.checkPredecessor(check_predecessor_request, timeout=20)
        except:
            print("[check_predecessor] Node#{} rpc error when to {}".format(self.id, predecessor[0]))
            self.set_predecessor(-1, "null")

    def sync_successor_list(self):
        print('[sync_successor_list] ',self.successor_list)
        successor = self.get_successor()
        if self.id == successor[0] or successor[0] == -1:
            return
        #Contact successor and update your own successor list
        #Eventually all entries will be filled
        #Good idea: Why not return Successor list when successor_predecessor rpc is called
        channel = grpc.insecure_channel(successor[1])
        stub = chord_pb2_grpc.ChordServiceStub(channel)
        request = chord_pb2.Empty()
        try:
            response = stub.getSuccessorList(request, timeout=10)

            new_list = [(node_info.id, node_info.ip) for node_info in response.succList]
            new_list.pop() # Delete last element
            new_list.insert(0, successor) # Prepend successor s

            print("[sync_successor_list] response received = " + str(new_list))
            old_list = self.get_successor_list()
            self.set_successor_list(new_list)

        except Exception as e:
            print(str(e))
            #Successor not alive
            print("[sync_successor_list] RPC failed")

            #Remove successor from successor list and take subsequent successor
            new_list = self.get_successor_list()
            new_list.pop(0)
            new_list.append((self.id, self.ip)) # Add ourself as a successor at the end. NOTE : Don't put -1 here
            old_list = self.get_successor_list()
            self.set_successor_list(new_list)
        
        old_list = set(old_list)
        new_list = set(new_list)
        if(set(old_list) != set(new_list)):
            self.onSuccessorListChanged(old_list, new_list)

    # Called whenever successorList is modified
    def onSuccessorListChanged(self, old_list, new_list):
        print("SUCCESSOR LIST CHANGED !")
        set_difference = new_list.difference(old_list)
        set_difference.discard((-1, 'null')) # Remove -1s
        set_difference.discard((self.id, self.ip)) # Remove ourself from the difference set

        print(f'DIFFERENCE = {set_difference}')
        if len(set_difference) != 0:
            # Transfer owner_list to all nodes in set_difference
            self.owner_lock.acquire()
            owner_dict = self.owner_dict.copy()
            self.owner_lock.release()
            for target in set_difference:
                ReplicateThread(self, target, owner_dict, 'replicated').start()


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
        successor = self.get_successor()
        predecessor = self.get_predecessor()
        if successor[0] == -1:
            return (-1,"null")
        if successor[0] == self.id and predecessor[0] == -1:
            return (self.id, self.ip)
        if successor[0] == self.id and predecessor[0] != -1:
            print("Updating successor")
            self.set_successor(predecessor[0], predecessor[1])
            return (self.id, self.ip)
        channel = grpc.insecure_channel(successor[1])
        stub = chord_pb2_grpc.ChordServiceStub(channel)
        request = chord_pb2.Empty()
        response = stub.findSuccessorsPred(request)
        return (response.id,response.ip)

    def serve(self):
        ip = '0.0.0.0:' + sys.argv[1]
        options = [('grpc.max_message_length', utils.max_message_length),('grpc.max_send_message_length', utils.max_message_length), ('grpc.max_receive_message_length', utils.max_message_length)]

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),options=options)
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
    node.fix_finger.start()
    node.serve()

if __name__ == "__main__":
    main()
    
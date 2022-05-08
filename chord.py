import hashlib
import grpc
from requests import request
import chord_pb2_grpc
import chord_pb2
import utils
from concurrent import futures
import os
from authentication import validate_signature
from chord_replicate import ReplicateThread

class ChordServicer(chord_pb2_grpc.ChordServiceServicer):

    def __init__(self, node):
        super().__init__()
        self.node = node

    def findSuccessor(self, request, context):
        response = chord_pb2.FindSuccessorResponse()

        # TODO: Handle case when this node is responsible for the request i.e. target_distance = 0
        print("[chord] findSuccessor id ",request.id)

        successor = self.node.get_successor()
        target_key = request.id
        target_distance = utils.circular_distance(self.node.id, target_key, self.node.ring_bits)
        successor_distance = utils.circular_distance(self.node.id, successor[0], self.node.ring_bits)
        if target_distance <= successor_distance:
            response.ip = successor[1]
            response.id = successor[0]
            response.is_final = True
            print("[chord] findSuccessor response")

            return response

        response.id, response.ip = self.node.closestPrecedingNode(target_key)
        if response.id == self.node.id:
            response.is_final = True
        else:
            response.is_final = False
        print("[chord] response id ",response.id)
        print("[chord] response addr ",response.ip)
        print("[chord] response is_final ",response.is_final)

        return response

    '''
    Finding successor's predecessor info
    '''
    def findSuccessorsPred(self, request, context):
        response = chord_pb2.FindSuccessorsPredResponse()
        predecessor = self.node.get_predecessor()
        response.ip = predecessor[1]
        response.id = predecessor[0]
        
        return response
    
    def notify(self, request, context):
        print("[notify_at_join] node {} received notify to set predecessor to {}".format(self.node.id, request.predecessorId))
        successor = self.node.get_successor()
        predecessor = self.node.get_predecessor()
        x_id, x_ip = request.predecessorId, request.addr # x is n'

        # Find keys in owner_dict that must be transferred to predecessor
        transfer_dict = {}
        x_n_distance = utils.circular_distance(x_id, self.node.id, self.node.ring_bits)
        self.node.owner_lock.acquire()
        for publickey_filename in self.node.owner_dict:
            fileid, checksum = self.node.owner_dict[publickey_filename]
            x_file_distance = utils.circular_distance(x_id, fileid, self.node.ring_bits)
            if not(x_file_distance <= x_n_distance and x_file_distance > 0):
                transfer_dict[publickey_filename] = (fileid, checksum)
        self.node.owner_lock.release()

        if predecessor[0] == -1:
            self.node.set_predecessor(x_id, x_ip)
            ReplicateThread(node = self.node, target = (x_id, x_ip),
                            replication_dict = transfer_dict, which_dict = 'owner').start()
        else:
            pred_x_distance = utils.circular_distance(predecessor[0], x_id, self.node.ring_bits)
            pred_n_distance = utils.circular_distance(predecessor[0], self.node.id, self.node.ring_bits)

            # If n' belongs to (pred, n) then set n.pred = n'
            if pred_x_distance < pred_n_distance and pred_x_distance != 0:
                self.node.set_predecessor(x_id, x_ip)
                ReplicateThread(node = self.node, target = (x_id, x_ip),
                                replication_dict = transfer_dict, which_dict = 'owner').start()
                # Set n.succ = n' to break self loop (happens when 2nd node joins chord)
                if successor[0] == self.node.id:
                    self.node.set_successor(x_id, x_ip)

        return chord_pb2.NotifyResponse(result=0)

    def checkPredecessor(self, request, context):
        print("[checkPredecessor] node {} received request".format(self.node.id))
        response = chord_pb2.Empty()
        return response
    
    def checkAlive(self, request, context):
        print("[Ping] node {} to check liveness ".format(self.node.id))
        response = chord_pb2.Empty()
        return response
    '''
    Debug RPC interface
    '''
    def debug(self, request, context):
        print('[chord] Inside debug')
        pred = chord_pb2.NodeInfo(id = self.node.predecessor[0], ip = self.node.predecessor[1])
        succ = chord_pb2.NodeInfo(id = self.node.successor[0], ip = self.node.successor[1])
        self_node = chord_pb2.NodeInfo(id = self.node.id, ip = self.node.ip)

        ftable_nodeinfo = [chord_pb2.NodeInfo(id = x[0], ip = x[1]) for x in self.node.ftable]
        response = chord_pb2.DebugInfo(predecessor = pred, successor = succ, self_node = self_node)
        response.ftable.extend(ftable_nodeinfo)
        return response

    def getSuccessorList(self, request, context):
        print("[chord] Get successor list",self.node.successor_list)
        succlist_nodeinfo = [chord_pb2.NodeInfo(id = x[0], ip = x[1]) for x in self.node.successor_list]
        response = chord_pb2.getSuccessorListResponse(succList = succlist_nodeinfo)
        return response

    def save_chunks_to_file(self, chunks, filename, pbkey_bytes):
        print('[chord] File save')
        target_filename = os.path.join(self.node.storage_dir, pbkey_bytes.hex())
        if not os.path.exists(target_filename):
            os.makedirs(target_filename) # Create Dir
        target_filename = os.path.join(target_filename, filename)
        with open(target_filename, 'wb') as f:
            for chunk in chunks:
                print(chunk.buffer)
                f.write(chunk.buffer)

    def putFile(self, request_iterator, context):
        print("[chord] File upload")
        info = ''
        file_name = None
        for chunk in request_iterator:
            print(chunk.buffer)
            info = chunk.buffer
            signature = info[:64]
            pbkey_bytes = info[64:64+91]
            file_name = info[64+91:].decode()
            
            # TODO : Match the public key with the one stored locally with data.
            
            if not validate_signature(signature,pbkey_bytes,file_name):
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details('Signature mismatch!')
                return chord_pb2.PutFileResponse()
            break

        self.save_chunks_to_file(request_iterator, file_name, pbkey_bytes)

        # Add this file to self.node.owner_dict
        hashkey = pbkey_bytes + file_name.encode()
        file_hash = int(hashlib.sha1(hashkey).hexdigest(), 16) % (2**self.node.ring_bits)
        publickey_filename = pbkey_bytes.hex() + '_' + file_name
        self.node.addToOwnerDict(publickey_filename, file_hash, 0)

        print(f'[chord] Put : Owner List = {self.node.owner_dict}')

        # Replicate this file to our successorList
        file_dict = {}
        file_dict[pbkey_bytes.hex() + '_' + file_name] = (file_hash, 0)
        succ_list = set(self.node.get_successor_list())
        succ_list.discard((-1, 'null'))
        succ_list.discard((self.node.id, self.node.ip))
        for target_node in succ_list:
            #print('[PUT] Replicating = ' + str(node) + ' , ' + str(file_dict))
            ReplicateThread(node = self.node, target = target_node,
                            replication_dict = file_dict,  which_dict = 'replicated').start()

        target_filename = os.path.join(self.node.storage_dir, pbkey_bytes.hex(), file_name)
        return chord_pb2.PutFileResponse(length=os.path.getsize(target_filename))

    def get_file_chunks(self, filename, pbkey_bytes):
        target_filename = os.path.join(self.node.storage_dir, pbkey_bytes.hex(), filename)
        with open(target_filename, 'rb') as f:
            while True:
                piece = f.read()
                if len(piece) == 0:
                    return
                yield chord_pb2.Chunk(buffer=piece)

    def getFile(self, request, context):
        print("[chord] Download request for file",request.name)    
        file_name = request.name
        signature = request.signature
        pbkey_bytes = request.publickey
        
        if not validate_signature(signature,pbkey_bytes,file_name):
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details('Signature mismatch!')
            print("[chord] Get request failed")
            return chord_pb2.Chunk()

        return self.get_file_chunks(request.name, pbkey_bytes)

    '''
    Called by another node to replicate a file on this node
    '''
    def replicateFile(self, request_iterator, context):
        publickey_filename = ''
        fileid = ''
        checksum = ''
        which_dict = ''

        for request in request_iterator:
            print('Inside request iterator!')
            publickey_filename = request.publickey_filename
            fileid = request.fileid
            checksum = request.checksum
            which_dict = request.which_dict
            break
        
        pbkey_str = publickey_filename[0:publickey_filename.find('_')]
        filename = publickey_filename[publickey_filename.find('_') + 1:]

        print('[chord] replicateFile RPC = ' + publickey_filename)

        target_filename = os.path.join(self.node.storage_dir, pbkey_str)
        if not os.path.exists(target_filename):
            os.makedirs(target_filename) # Create Dir
        target_filename = os.path.join(target_filename, filename)
        with open(target_filename, 'wb') as f:
            for request in request_iterator:
                print(request.buffer)
                f.write(request.buffer)
        
        if which_dict == 'replicated':
            # Add it to our replicated dict
            print('[replicateFile] Adding to replicated dict = ' + publickey_filename)
            self.node.addToReplicatedDict(publickey_filename, fileid, checksum)
        elif which_dict == 'owner':
            # Add to our owner dict
            print('[replicateFile] Adding to owner dict = ' + publickey_filename)
            self.node.addToOwnerDict(publickey_filename, fileid, checksum)


        return chord_pb2.Empty()


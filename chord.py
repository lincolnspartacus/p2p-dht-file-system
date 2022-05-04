import grpc
import chord_pb2_grpc
import chord_pb2
import utils
from concurrent import futures
import os

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

        if predecessor[0] == -1:
            self.node.set_predecessor(request.predecessorId, request.addr)
        else:
            x_id, x_ip = request.predecessorId, request.addr # x is n'
            pred_x_distance = utils.circular_distance(predecessor[0], x_id, self.node.ring_bits)
            pred_n_distance = utils.circular_distance(predecessor[0], self.node.id, self.node.ring_bits)

            # If n' belongs to (pred, n) then set n.pred = n'
            if pred_x_distance < pred_n_distance and pred_x_distance != 0:
                self.node.set_predecessor(x_id, x_ip)
                # Set n.succ = n' to break self loop (happens when 2nd node joins chord)
                if successor[0] == self.node.id:
                    self.node.set_successor(x_id, x_ip)

        # TODO: Transfer of keys on join. refer 
        return chord_pb2.NotifyResponse(result=0)

    def checkPredecessor(self, request, context):
        print("[checkPredecessor] node {} received request".format(self.node.id))
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

    def save_chunks_to_file(self, chunks, filename):
        print('[chord] File save')
        with open(self.node.storage_dir+filename, 'wb') as f:
            for chunk in chunks:
                print(chunk.buffer)
                f.write(chunk.buffer)

    def upload(self, request_iterator, context):
        print("[chord] File upload")
        # TODO : Add suppport for sending file name, key value, public key 
        # in first chunk
        info = ''
        for chunk in request_iterator:
            print(chunk.buffer)
            info = chunk.buffer
            break
        file_name = info.decode()
        self.save_chunks_to_file(request_iterator, file_name)
        
        return chord_pb2.Reply(length=os.path.getsize(self.node.storage_dir+file_name))

    def get_file_chunks(self, filename):
        with open(self.node.storage_dir+filename, 'rb') as f:
            while True:
                piece = f.read()
                if len(piece) == 0:
                    return
                yield chord_pb2.Chunk(buffer=piece)

    def download(self, request, context):
        print("[chord] Download request for file",request.name)    
        return self.get_file_chunks(request.name)

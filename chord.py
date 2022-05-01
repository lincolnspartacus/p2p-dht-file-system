import grpc
import chord_pb2_grpc
import chord_pb2
import utils
from concurrent import futures

class ChordServicer(chord_pb2_grpc.ChordServiceServicer):

    def __init__(self, node):
        super().__init__()
        self.node = node

    def findSuccessor(self, request, context):
        response = chord_pb2.FindSuccessorResponse()

        # TODO: Handle case when this node is responsible for the request i.e. target_distance = 0
        print("[chord] findSuccessor id ",request.id)

        target_key = request.id
        target_distance = utils.circular_distance(self.node.id, target_key, self.node.ring_bits)
        successor_distance = utils.circular_distance(self.node.id, self.node.successor[0], self.node.ring_bits)
        if target_distance <= successor_distance:
            response.ip = self.node.successor[1]
            response.id = self.node.successor[0]
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
        response.ip = self.node.predecessor[1]
        response.id = self.node.predecessor[0]
        
        return response
    
    def notify(self, request, context):
        print("[notify_at_join] node {} received notify to set predecessor to {}".format(self.node.id, request.predecessorId))
        if self.node.predecessor[0] == -1:
            self.node.set_predecessor(request.predecessorId, request.addr)
        else:
            x_id, x_ip = request.predecessorId, request.addr # x is n'
            pred_x_distance = utils.circular_distance(self.node.predecessor[0], x_id, self.node.ring_bits)
            pred_n_distance = utils.circular_distance(self.node.predecessor[0], self.node.id, self.node.ring_bits)

            # If n' belongs to (pred, n) then set n.pred = n'
            if pred_x_distance < pred_n_distance and pred_x_distance != 0:
                self.node.set_predecessor(x_id, x_ip)
                # Set n.succ = n' to break self loop (happens when 2nd node joins chord)
                if self.node.successor[0] == self.node.id:
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
        #succlist_nodeinfo = []
        #for i, x in enumerate(self.node.successor_list):
        #    entry = chord_pb2.NodeInfo(x[0],x[1])
        #    succlist_nodeinfo.append(entry)
        #deep_succlist = deepcopy(self.successor_list)
        succlist_nodeinfo = [chord_pb2.NodeInfo(id = x[0], ip = x[1]) for x in self.node.successor_list]
        #print(succlist_nodeinfo)
        response = chord_pb2.getSuccessorListResponse(succList = succlist_nodeinfo)
        return response

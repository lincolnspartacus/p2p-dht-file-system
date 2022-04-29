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
            response.id = str(self.node.successor[0])
            response.is_final = True
            print("[chord] findSuccessor response")

            return response

        response.id, response.ip = self.node.closestPrecedingNode(target_key)
        response.is_final = False
        print("[chord] response id ",response.id)
        print("[chord] response addr ",response.ip)
        print("[chord] response is_final ",response.is_final)

        return response

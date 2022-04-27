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
        target_key = request.id
        target_distance = utils.circular_distance(self.node.id, target_key, self.node.ring_bits)
        successor_distance = utils.circular_distance(self.node.id, self.successor[0], self.node.ring_bits)
        if target_distance <= successor_distance:
            response.ip = self.successor[1]
            response.id = self.successor[0]
            response.is_final = True

            return response

        response.id, response.ip = self.node.closestPrecedingNode(target_key)
        response.is_final = False

        return response

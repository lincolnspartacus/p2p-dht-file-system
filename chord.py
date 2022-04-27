import grpc
import chord_pb2_grpc
import chord_pb2
from concurrent import futures

class ChordServicer(chord_pb2_grpc.ChordServiceServicer):

    def findSuccessor(self, request, context):
        response = chord_pb2.FindSuccessorResponse(addr = "0.0.0.0:50051")
        print(f"Inside findSuccessor, id = {request.id}")

        return response

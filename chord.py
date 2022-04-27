import grpc
import chord_pb2_grpc
import chord_pb2
from concurrent import futures

class ChordServicer(chord_pb2_grpc.ChordServiceServicer):

    def findSuccessor(self, request, context):
        response = chord_pb2.FindSuccessorResponse(addr = "0.0.0.0:50051")
        print(f"Inside findSuccessor, id = {request.id}")

        return response

def serve(ip):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chord_pb2_grpc.add_ChordServiceServicer_to_server(
        ChordServicer(), server)
    server.add_insecure_port(ip)
    server.start()

    print(f'[chord] Listening on {ip}')
    server.wait_for_termination()

if __name__ == "__main__":
    serve('[::]:50051')
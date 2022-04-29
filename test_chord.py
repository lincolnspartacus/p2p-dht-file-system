import grpc
import chord_pb2_grpc
import chord_pb2

def main():
    print("Trying to reach the chord server..")
    channel = grpc.insecure_channel('localhost:50051')
    stub = chord_pb2_grpc.ChordServiceStub(channel)

    request = chord_pb2.FindSuccessorRequest(id = 5235)
    response = stub.findSuccessor(request)
    print(f"Response address = {response.ip}")

if __name__ == "__main__":
    main()
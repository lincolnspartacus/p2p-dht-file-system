import grpc
import chord_pb2_grpc
import chord_pb2

def main():
    print("Trying to reach the chord server..")
    channel = grpc.insecure_channel('localhost:50051')
    stub = chord_pb2_grpc.ChordServiceStub(channel)

    # request = chord_pb2.FindSuccessorRequest(id = 5235)
    # response = stub.findSuccessor(request)
    # print(f"Response address = {response.ip}")

    # Debug interface
    request = chord_pb2.Empty()
    response = stub.debug(request)
    print('*****************************')
    print('Node = ({0}, {1})'.format(response.self_node.id, response.self_node.ip))
    print('Successor = ({0}, {1})'.format(response.successor.id, response.successor.ip))
    print('Predecessor = ({0}, {1})'.format(response.predecessor.id, response.predecessor.ip))
    print('FTable = ')
    for i, node_info in enumerate(response.ftable):
        print('FTable[{0}] = ({1}, {2})'.format(str(i), node_info.id, node_info.ip))
    print('*****************************')

if __name__ == "__main__":
    main()
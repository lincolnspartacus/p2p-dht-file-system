import grpc
import chord_pb2_grpc
import chord_pb2

def printDetails(ip):
    channel = grpc.insecure_channel(ip)
    stub = chord_pb2_grpc.ChordServiceStub(channel)

    # Debug interface
    request = chord_pb2.Empty()
    response = stub.debug(request)
    print('*****************************')
    print('Node = ({0}, {1})'.format(response.self_node.id, response.self_node.ip))
    print('Successor = ({0}, {1})'.format(response.successor.id, response.successor.ip))
    print('Predecessor = ({0}, {1})'.format(response.predecessor.id, response.predecessor.ip))
    # print('FTable = ')
    # for i, node_info in enumerate(response.ftable):
    #     print('FTable[{0}] = ({1}, {2})'.format(str(i), node_info.id, node_info.ip))
    print('Owner List = ' + response.ownerList)
    print('Replicated List = ' + response.replicatedList)
    print('*****************************')


def main():
    print("Trying to reach the chord server..")
    nodes = ['0.0.0.0:50050', '0.0.0.0:50055', '0.0.0.0:50056', '0.0.0.0:50057']

    for node in nodes:
        try:
            printDetails(node)
        except:
            pass

if __name__ == "__main__":
    main()
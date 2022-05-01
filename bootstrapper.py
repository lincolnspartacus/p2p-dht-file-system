import grpc
import chord_pb2_grpc
import chord_pb2
import random
from concurrent import futures

class BootstrapServicer(chord_pb2_grpc.BootstrapServiceServicer):
    def __init__(self):
        super().__init__()
        self.table = [] # Stores node info in (ID, IP addr) format
    
    '''
    Picks a random node from the tracker table and returns it
    '''
    def getNode(self, request, context):
        response = chord_pb2.NodeInfo()
        response.id = -1
        response.ip = "null"
        if len(self.table) > 0:
            node = random.choice(self.table)
            response.id = node[0]
            response.ip = node[1]

        print(f'[tracker] Inside getNode = ({response.id}, {response.ip})')
        return response

    '''
    Adds the given node to the tracker table
    '''
    def addNode(self, request, context):
        response = chord_pb2.Empty()
        table_entry = (request.id, request.ip)
        print(f'[tracker] Inside addNode = {table_entry}')
        if table_entry not in self.table:
            self.table.append(table_entry)
        return response
    
    '''
    Clears the tracker table (debugging only!)
    '''
    def clearTable(self, request, context):
        response = chord_pb2.Empty()
        self.table.clear()
        print('[tracker] Clearing table')
        return response

def main():
    ip = 'localhost:40051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chord_pb2_grpc.add_BootstrapServiceServicer_to_server(BootstrapServicer(), server)
    server.add_insecure_port(ip)
    server.start()

    print(f'[tracker] Listening on {ip}')
    server.wait_for_termination()

if __name__ == "__main__":
    main()

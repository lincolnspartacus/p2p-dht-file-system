import grpc
import chord_pb2_grpc
import chord_pb2
import random
from concurrent import futures
import threading

class BootstrapServicer(chord_pb2_grpc.BootstrapServiceServicer):
    def __init__(self):
        super().__init__()
        self.table = {} # Stores node info in (ID, IP addr) format
        self.node_counter = 0
        self.tbLock = threading.Lock()

    '''
    Picks a random node from the tracker table and returns it
    '''
    def getNode(self, request, context):
        response = chord_pb2.NodeInfo()
        response.id = -1
        response.ip = "null"

        self.tbLock.acquire()
        keyList = self.table.keys()
        self.tbLock.release()
        random.shuffle(keyList)

        for key in keyList:
            try:
                self.tbLock.acquire()
                targetIP = self.table[key]
                self.tbLock.release()
            except:
                continue
            try:
                channel = grpc.insecure_channel(targetIP)
                stub = chord_pb2_grpc.ChordServiceStub(channel)
                request = chord_pb2.Empty()
                stub.checkAlive(request,timeout=5)
                response.id = key
                response.ip = targetIP
                print(f'[tracker] Inside getNode = ({response.id}, {response.ip})')
                return response

            except:
                self.tbLock.acquire()
                self.table.pop(key,None)
                self.tbLock.release()

        print(f'[tracker] Inside getNode = ({response.id}, {response.ip})')
        return response

    '''
    Adds the given node to the tracker table
    '''
    def addNode(self, request, context):
        response = chord_pb2.Empty()
        table_entry = (request.id, request.ip)
        print(f'[tracker] Inside addNode = {table_entry}')

        self.tbLock.acquire()
        if table_entry[0] not in self.table:
            self.table[table_entry[0]] = table_entry
        self.tbLock.release()

        return response
    
    '''
    Clears the tracker table (debugging only!)
    '''
    def clearTable(self, request, context):
        response = chord_pb2.Empty()
        
        self.tbLock.acquire()
        self.table.clear()
        self.tbLock.release()

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

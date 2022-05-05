import chord
import socket
import threading
import hashlib
import utils
import grpc
import sys
import chord_pb2_grpc
import chord_pb2
import os

CHUNK_SIZE = 1024 * 1024  # 1MB
class ChordClient():
    def __init__(self, client):
        # TODO: Enable getting ip port from user
        self.client_ip = '0.0.0.0:' + '40044' #Hardcoded for now 
        self.ring_bits = 16 #Can get it from bootstrapper every time on get/put request
        self.bootstrapper_ip = 'localhost:40051'
        self.client = client

    def contactBootstrapper(self):
        channel = grpc.insecure_channel(self.bootstrapper_ip)
        stub = chord_pb2_grpc.BootstrapServiceStub(channel)
        request = chord_pb2.Empty()

        response = stub.getNode(request)
        print(f'[chord_client] contactBootstrapper returned ({response.id}, {response.ip})')
        return (response.id, response.ip)

    def get_file_chunks(self, filename):
        print("[chord_client] get_file_chunks")
        # TODO : Add key, public key info in the first chunk
        key=filename.encode()
        yield chord_pb2.Chunk(buffer=key)
        with open(self.client.storage_path+filename, 'rb') as f:
            while True:
                piece = f.read()
                if len(piece) == 0:
                    return
                print(piece)
                yield chord_pb2.Chunk(buffer=piece)

    def save_chunks_to_file(self, chunks, filename):
        with open(filename, 'wb') as f:
            for chunk in chunks:
                f.write(chunk.buffer)

    def find_responsible_node(self,key,target_ip):

        is_final = False
        while not is_final:
            channel = grpc.insecure_channel(target_ip)
            stub = chord_pb2_grpc.ChordServiceStub(channel)
            request = chord_pb2.FindSuccessorRequest(id = key)
            response = stub.findSuccessor(request)
            target_ip = response.ip
            is_final = response.is_final

        return response

    def put(self, filename):
        '''
        Returns 0 on success, -1 on failure
        Compute hash value for filename
        Contact bootstrapper node for a random node
        Do a lookup for the node that is responsible for the key 
        Contact the node directly and complete the get call
        TODO: If node crashes in the middle, start again
        TODO: If key doesnt exist, have different failure in RPC call
        '''
        req_node = self.contactBootstrapper()
        
        if req_node[0] == -1:
            return -1

        file_hash = int(hashlib.sha1(filename.encode('utf-8')).hexdigest(), 16) % (2**self.ring_bits)
        print("[Chord Client] File Hash",file_hash)

        response = self.find_responsible_node(file_hash, req_node[1])
        print("[Chord Client] findSuccessor response",response)

        options = [('grpc.max_message_length', 100 * 1024 * 1024),('grpc.max_send_message_length', 512 * 1024 * 1024), ('grpc.max_receive_message_length', 512 * 1024 * 1024)]
        channel = grpc.insecure_channel(response.ip,options =options)
        # TODO : Try/except logic on communication with nodes
        stub = chord_pb2_grpc.ChordServiceStub(channel)
        chunks_generator = self.get_file_chunks(filename)

        response = stub.putFile(chunks_generator)
        #Enable assertion?
        #assert response.length == os.path.getsize(in_file_name)
        return 0

    def get(self, filename):
        '''
        Returns 0 on success, -1 on failure
        Compute hash value for filename
        Contact bootstrapper node for a random node
        Do a lookup for the node that is responsible for the key 
        Contact the node directly and complete the get call
        TODO : If node crashes in the middle, start again
        TODO : If key doesnt exist, have different failure in RPC call
        '''
        req_node = self.contactBootstrapper()
        
        if req_node[0] == -1:
            return -1

        file_hash = int(hashlib.sha1(filename.encode('utf-8')).hexdigest(), 16) % (2**self.ring_bits)
        print("[Chord Client] File Hash",file_hash)
        response = self.find_responsible_node(file_hash, req_node[1])
        print("[Chord Client] findSuccessor response",response)
       
        # TODO : Fix for large files required, max messsage length not sufficient
        options = [('grpc.max_message_length', 100 * 1024 * 1024),('grpc.max_send_message_length', 512 * 1024 * 1024), ('grpc.max_receive_message_length', 512 * 1024 * 1024)]
        channel = grpc.insecure_channel(response.ip, options=options)
        stub = chord_pb2_grpc.ChordServiceStub(channel)
        response = stub.getFile(chord_pb2.GetFileRequest(name=filename))
        target_file_name = self.client.storage_path + filename
        self.save_chunks_to_file(response, target_file_name)
        #assert response.length == os.path.getsize(in_file_name)
        return 0

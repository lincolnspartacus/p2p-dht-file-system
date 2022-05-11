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
from authentication import Auth

CHUNK_SIZE = 1024 * 1024  # 1MB
class ChordClient():
    def __init__(self, storage_path,key_path=""):
        # TODO: Enable getting ip port from user
        self.client_ip = '0.0.0.0:' + '40044' #Hardcoded for now 
        self.ring_bits = 16 #Can get it from bootstrapper every time on get/put request
        self.bootstrapper_ip = 'localhost:40051'
        self.storage_path = storage_path

        if key_path!="":
            self.key_path = key_path
        else:
            self.key_path = os.path.join(storage_path,"keys")
        
        if not os.path.exists(self.key_path):
            os.makedirs(self.key_path)
        self.auth = Auth(self.key_path)

    def contactBootstrapper(self):
        channel = grpc.insecure_channel(self.bootstrapper_ip)
        stub = chord_pb2_grpc.BootstrapServiceStub(channel)
        request = chord_pb2.Empty()

        response = stub.getNode(request)
        print(f'[chord_client] contactBootstrapper returned ({response.id}, {response.ip})')
        return (response.id, response.ip)

    def get_file_chunks(self, filename, signature, pbkey_bytes):
        print("[chord_client] get_file_chunks")
        
        absolute_path = filename
        filename = os.path.basename(absolute_path)
        #signature+publickey+filename:91+64bytes+filename
        key=signature+pbkey_bytes+filename.encode()
        yield chord_pb2.Chunk(buffer=key)

        with open(absolute_path, 'rb') as f:
            while True:
                piece = f.read(utils.chunk_size)
                if len(piece) == 0:
                    return
                print(piece)
                yield chord_pb2.Chunk(buffer=piece)

    def save_chunks_to_file(self, chunks, filename):
        f = open(filename, 'wb')
        
        for chunk in chunks:
            print(chunk.buffer)
            f.write(chunk.buffer)

        f.close()

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

        signature = self.auth.sign_message(filename.encode())
        pbkey_bytes = self.auth.get_publickey()
        # Concat publickey,filename for hashing
        hashkey = pbkey_bytes+filename.encode()

        file_hash = int(hashlib.sha1(hashkey).hexdigest(), 16) % (2**self.ring_bits)
        print("[Chord Client] File Hash",file_hash)

        response = self.find_responsible_node(file_hash, req_node[1])
        print("[Chord Client] findSuccessor response",response)

        options = [('grpc.max_message_length', 100 * 1024 * 1024),('grpc.max_send_message_length', 512 * 1024 * 1024), ('grpc.max_receive_message_length', 512 * 1024 * 1024)]
        channel = grpc.insecure_channel(response.ip,options =options)
        # TODO : Try/except logic on communication with nodes
        stub = chord_pb2_grpc.ChordServiceStub(channel)

        chunks_generator = self.get_file_chunks(filename,signature,pbkey_bytes)
        
        try:
            response = stub.putFile(chunks_generator)
        except grpc.RpcError as e:
            print(e)
            e.details()
            status_code = e.code()
            status_code.name
            status_code.value
            return -1
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

        signature = self.auth.sign_message(filename.encode())
        pbkey_bytes = self.auth.get_publickey()
        # Concat (publickey,filename) for hashing
        hashkey = pbkey_bytes+filename.encode()

        file_hash = int(hashlib.sha1(hashkey).hexdigest(), 16) % (2**self.ring_bits)
        print("[Chord Client] File Hash",file_hash)
        response = self.find_responsible_node(file_hash, req_node[1])
        print("[Chord Client] findSuccessor response",response)
       
        options = [('grpc.max_message_length', 100 * 1024 * 1024),('grpc.max_send_message_length', 512 * 1024 * 1024), ('grpc.max_receive_message_length', 512 * 1024 * 1024)]
        channel = grpc.insecure_channel(response.ip, options=options)
        stub = chord_pb2_grpc.ChordServiceStub(channel)
        
        ## Generate a modified key. For testing
        #pbkey_bytes = self.auth.modified_key()

        try:
            response = stub.getFile(chord_pb2.GetFileRequest(name=filename,signature=signature,publickey=pbkey_bytes))
        except grpc.RpcError as e:
            e.details()
            status_code = e.code()
            status_code.name
            status_code.value
            return -1

        target_file_name = os.path.join(self.storage_path,filename)
        self.save_chunks_to_file(response, target_file_name)

        return 0

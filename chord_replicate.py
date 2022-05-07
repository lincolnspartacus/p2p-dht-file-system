from threading import Thread
import chord_pb2_grpc
import chord_pb2
import grpc
import os

class ReplicateThread(Thread):

    def __init__(self, node, target, replication_dict):
        Thread.__init__(self)
        self.node = node # Our own node object
        self.target = target # Target node for replication (id, ip)
        self.replication_dict = replication_dict # Files to be replicated
    
    def getChunks(self, publickey_filename, fileid, checksum):
        targetFileName = publickey_filename.replace('_', '/', 1)
        targetFileName = os.path.join(self.node.storage_dir, targetFileName)

        req = chord_pb2.ReplicateRequest()
        req.publickey_filename = publickey_filename
        req.fileid = str(fileid)
        req.checksum = str(checksum)
        yield req

        with open(targetFileName, 'rb') as f:
            while True:
                req = chord_pb2.ReplicateRequest()
                piece = f.read()
                if len(piece) == 0:
                    return
                req.buffer = piece
                yield req

    def run(self):
        channel = grpc.insecure_channel(self.target[1])
        stub = chord_pb2_grpc.ChordServiceStub(channel)

        for publickey_filename in self.replication_dict:
            fileid = self.replication_dict[publickey_filename][0]
            checksum = self.replication_dict[publickey_filename][1]
            replicateGenerator = self.getChunks(publickey_filename, fileid, checksum)
            response = stub.replicateFile(replicateGenerator)


        
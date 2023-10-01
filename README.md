Packages
================

Run ./setup.sh for installing pip packages

Code Structure
================
authentication.py - Cryptographic module for client authentication  
bootstrapper.py - Bootstrapper that returns IP of an existing node in the ring  
chord_client.py - Client Library  
chord_pb2_grpc.py - Autogen gRPC file  
chord_pb2.py - Autogen gRPC file  
chord.py - Implementation of all RPCs()  
chord_replicate.py - Code that spawns a thread for asynchronous key replication  
client.py - Our test client  
debug.py - Dumps state of all nodes in the ring for debugging (over RPC)  
fix_finger.py - Thread that periodically fixes the finger table  
node.py - Implementation of the Node class  
stabilize.py - Thread that periodically runs chord's stabilize() + sync_successor_list() + check_predecessor()  
utils.py - Utility functions for modulo arithmetic etc  
  
Execute 'make' to rebuild any proto files  
  
Bootstrapper  
================
  
Before starting any node, we must start the bootstrapper.  

python bootstrapper.py  
  
The bootstrapper is assumed to never crash and does not participate  
in any requests. It is only used to join the Chord ring.  
  
Firing up nodes  
=================
  
The code has been currently set to run everything on localhost.  
Fire up a node by executing this command -   
  
python node.py <port number>  
  
For example -   
python node.py 50050  
python node.py 50055  
python node.py 50056  
python node.py 50057  
  
These port number values will recreate the NodeIDs mentioned in our PPT/Report.

Client  
=================

Clients can perform 2 operations - get() and put()  

Syntax :   
python client.py get <path-to-file>  
python client.py put <path-to-file>  
  
For example -   

python client.py put send_data/calvin.mp3  
  
Verifying correctness  
=================  

Our Chord interface exposes a debug() RPC for observing the current state of nodes in the ring.

First set the IP addresses of your nodes in debug.py:L26  
Run directly if you're using the 4 port numbers mentioned earlier.  
  
python debug.py  
  
It should print out all pointers, keys, finger table entries etc.  
  
Furthermore, you should see a new directories created for each Node that was booted up. For example - 
8299/  
10822/  
18541/  
38526/  
  
For each public key (user), we create a subdirectory that contains all the files
8299/  
    .ownerList  
    .replicatedList  
    public-key-1/  
        calvin.mp3  
  
.ownerList and .replicatedList are the pickle dumps of their in-memory counterparts  

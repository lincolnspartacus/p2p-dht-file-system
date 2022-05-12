from chord_client import ChordClient
import os,sys

def main():
    print("[Client]")

    # Local path for storing getfiles in (local_path/) and cryptography keys(local_path/.keys/)    
    local_path = "client_data/"
    client = ChordClient(local_path)
    filename = sys.argv[2]
    operation = sys.argv[1]

    if operation=='put':

        status = client.put(filename)
        if status == 0:
            print("Put request: Success")
        else:
            print("put failed")

    if operation=='get':
        # Get call  will result on data on local_path
        status = client.get(filename)
        if status == 0:
            print("Get request: Success")
        else:
            print("get failed")
            
if __name__ == "__main__":
    main()

from chord_client import ChordClient
import os,sys

def main():
    print("[Client]")

    # Local path for storing getfiles in (local_path/) and cryptography keys(local_path/.keys/)    
    local_path = "client_data/"
    client = ChordClient(local_path)
    
    send_path = "send_data/"
    fl_id = int(sys.argv[1])

    put=1
    if put==1:

        status = client.put(os.path.join(send_path,"large_file_"+str(fl_id)))
        if status == 0:
            print("Put request: Success")
        else:
            print("put failed")
    get=1
    if get==1:
        # Get call  will result on data on local_path
        status = client.get("large_file")
        if status == 0:
            print("Get request: Success")
        else:
            print("get failed")
            
if __name__ == "__main__":
    main()

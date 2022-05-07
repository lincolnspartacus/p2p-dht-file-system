from chord_client import ChordClient

def main():
    print("[Client]")

    # Local path for storing getfiles in (local_path/) and cryptography keys(local_path/.keys/)    
    local_path = "client_data/"
    client = ChordClient(local_path)
    
    status = client.put("LICENSE")
    if status == -1:
        print("put failed")
    else:
        print("Put request: Success")
    
    status = client.put("abc.txt")
    if status == -1:
        print("put failed")
    else:
        print("Put request: Success")
    
    #Get call  will result on data on local_path
    # status = client.get("abc.txt")
    # if status == -1:
    #     print("get failed")
    # else:
    #     print("Get request: Success")
        
if __name__ == "__main__":
    main()
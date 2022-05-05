from chord_client import ChordClient

class Client():
    def __init__(self):
        self.client_lib = ChordClient(self)
        self.storage_path = "client_data/"


def main():
    print("[Client]")
    client = Client()
    status = client.client_lib.put("abc.txt")
    #Get call  will result on data on self.storage_path
    status = client.client_lib.get("abc.txt")

if __name__ == "__main__":
    main()
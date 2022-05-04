from chord_client import ChordClient

class Client():
    def __init__(self):
        self.client_lib = ChordClient(self)
        self.storage_path = "client_data/"


def main():
    print("[Client]")
    client = Client()
    status,data = client.client_lib.put("abc.txt")
    status,data = client.client_lib.get("abc.txt")

if __name__ == "__main__":
    main()
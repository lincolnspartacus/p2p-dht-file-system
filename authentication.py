from email import message
import os
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import hashlib

class Auth():
    def __init__(self, path):
        self.keyfile = os.path.join(path,'myprivatekey.pem')

        if os.path.exists(self.keyfile):
            f = open(self.keyfile,'rt')
            self.private_key = ECC.import_key(f.read())  
        else:
            self.private_key = ECC.generate(curve='P-256')
            f = open(os.path.join(path,'myprivatekey.pem'),'wt')
            f.write(self.private_key.export_key(format='PEM'))
            f.close()

        self.public_key = self.private_key.public_key()
        self.pbkey_bytes = self.public_key.export_key(format='DER')

    def get_publickey(self):
        return self.pbkey_bytes

    def sign_message(self,message):
        h = SHA256.new(message)
        signer = DSS.new(self.private_key, 'fips-186-3') # Signature = Private key + Hash(Message)
        signature = signer.sign(h)
        return signature


def validate_signature(signature,pbkey_bytes,file_name):
    
    message = file_name.encode()
    hashkey = SHA256.new(message)
    
    public_key = ECC.import_key(pbkey_bytes)
    verifier = DSS.new(public_key, 'fips-186-3')
    try:
        verifier.verify(hashkey, signature)
        print("[Server] The message is authentic.")
    except ValueError:
        print("[Server] The message is not authentic.")
        return False
    return True
from base64 import b64encode, b64decode
import json
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
import codecs

def sign_data(private_key, data):
    # Check if the given data is in dictionary format, if not convert it
    if not isinstance(data, dict):
        data = {"data": data}
    # create "signature" key in given data dictionary before signing
    data["signature"] = ""
    data_hash = SHA256.new(json.dumps(data, sort_keys=True).encode('utf8'))
 
    # Load private key and sign message
    key = RSA.importKey(private_key)
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(data_hash)
    data["signature"] = signature.decode('ISO-8859-1')
    return data
    

def verify_signature(public_key, data):
    # Check if the given data is in dict form and "signature" key is present
    if not isinstance(data, dict) and "signature" not in data.keys():
        return False
    
    sig = data["signature"].encode('ISO-8859-1')
    data["signature"] = ""
    key = RSA.importKey(public_key)
    data_hash = SHA256.new(json.dumps(data, sort_keys=True).encode('utf8'))
    verifier = PKCS1_v1_5.new(key)
    return verifier.verify(data_hash, sig)

# keys = wallets.get_wallet()
# d = {"data" : "hello"}
# private_key = keys["private_key_string"]
# public_key = keys["public_key_string"]

# print(sign_data(private_key, d, public_key))

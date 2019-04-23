import json
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import binascii


# Verify txn with public key of sender and signature verification
def verify_signature(public_key_string, data):
    """
    Check that the provided signature corresponds to transaction
    signed by the public key (sender_address)
    """
    if not isinstance(data, dict) and "signature" not in data.keys():
        return False
    signature = data["signature"]
    data["signature"] = ""
    public_key = RSA.importKey(binascii.unhexlify(public_key_string))
    verifier = PKCS1_v1_5.new(public_key)
    h = SHA.new(json.dumps(data, sort_keys=True).encode('utf8'))
    data["signature"] = signature
    return verifier.verify(h, binascii.unhexlify(signature))


# Verify txn with public key of sender and signature verification
def sign_data(private_key_string, data):
    """
    Sign transaction with private key
    """
    private_key = RSA.importKey(binascii.unhexlify(private_key_string))
    signer = PKCS1_v1_5.new(private_key)

    if not isinstance(data, dict):
        data = {"data": data}
    data["signature"] = ""

    h = SHA.new(json.dumps(data, sort_keys=True).encode('utf8'))
    signature = binascii.hexlify(signer.sign(h)).decode('ascii')
    data["signature"] = signature
    return data



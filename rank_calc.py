import binascii
from hashlib import sha256
import json 

def rank_calc(prev_block_header, stake, prestige, public_key):
    return int(binascii.hexlify(sha256(str(public_key + prev_block_header["nonce"] + str(sha256(json.dumps(prev_block_header, sort_keys=True).encode('utf8')).hexdigest())).encode('utf8')).hexdigest().encode('utf8')), 16)/ ((stake + 10*prestige)**5)
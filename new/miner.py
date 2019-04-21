from blockchain_1 import Blockchain
from time import sleep
from datetime import datetime
from hashlib import sha256
import json
import binascii
from merkle import merkle_root

def mine(stake, public_key):
    blockchain = Blockchain()
    while stake > 0:
        last_block_header = blockchain.get_last_block()["header"]
        txns = blockchain.get_txns()
        txns.append({"type" : 0, "amount" : 10, "receiver" : public_key})
        txns.append({"type" : -1, "receiver" : public_key})
        header = get_header(txns, last_block_header, stake, public_key)
        # stake_val = int(binascii.hexlify(sha256(str(public_key + header["nonce"] + str(sha256(json.dumps(header, sort_keys=True).encode('utf8')).hexdigest())).encode('utf8')).hexdigest().encode('utf8')), 16)/(stake*blockchain.get_prestige())
        stake_val = int(last_block_header["nonce"]) / (stake * blockchain.get_prestige()) 
        # blockchain.add_block({"header" : header, "txns" : txns}, rand_val)
        print({"header" : header, "txns" : txns}, stake_val)
        sleep(60)

def get_header(txns, last_block_header, stake, public_key):
    return {
            "index" : last_block_header["index"], 
            "time" : str(datetime.now().time()),
            "nonce" : str(int(binascii.hexlify(sha256((public_key + sha256(json.dumps(last_block_header, sort_keys=True).encode('utf8')).hexdigest()).encode('utf8')).hexdigest().encode('utf8')), 16))[:32],
            "prev_hash" : sha256(json.dumps(last_block_header, sort_keys=True).encode('utf8')).hexdigest(),
            "stake" : stake,
            "miner" : public_key,
        #     "merkle" : sha256(json.dumps(txns, sort_keys=True).encode('utf8')).hexdigest()  
            "merkle": merkle_root(txns)        
        }

mine(10, "1EUhfrdDiSnL7bcATvtExQ1PruWMhfwwvV")

import sys
import os
from pathlib import Path
sys.path.append(str(Path(os.path.dirname(os.path.abspath(__file__))).parent)+'/merkle')
from time import sleep
from datetime import datetime
from hashlib import sha256
import json
import binascii
from merkle import merkle_root
from rank_calc import rank_calc
from blockchain import Blockchain


def mine(stake, public_key):
    blockchain = Blockchain.get_instance()
    while stake > 0:
        sleep(1)
        last_block_header = blockchain.get_last_block()["header"]
        txns = blockchain.get_txns()
        # txns.append({"type" : 0, "amount" : 10, "receiver" : public_key})
        # txns.append({"type" : -1, "receiver" : public_key})
        tmp_txn = {"type": 0, "amount": 10, "receiver": public_key, "time": str(datetime.now().time())}
        tmp_txn_hash = sha256(json.dumps(tmp_txn, sort_keys=True).encode('utf8')).hexdigest()
        tmp_prestige_txn = {"type": -1, "receiver": public_key, "time": str(datetime.now().time())}
        tmp_prestige_txn_hash = sha256(json.dumps(tmp_prestige_txn, sort_keys=True).encode('utf8')).hexdigest()
        txns[tmp_txn_hash] = tmp_txn
        txns[tmp_prestige_txn_hash] = tmp_prestige_txn
        header = get_header(txns, last_block_header, stake, public_key, blockchain.get_prestige(public_key))
        # stake_val = int(binascii.hexlify(sha256(str(public_key + header["nonce"] + str(sha256(json.dumps(header, sort_keys=True).encode('utf8')).hexdigest())).encode('utf8')).hexdigest().encode('utf8')), 16)/(stake*blockchain.get_prestige())
        rank = rank_calc(last_block_header, stake, header["prestige"], public_key)
        blockchain.add_miners_block({"header": header, "rank": rank, "txn": txns})
        sleep(10)


def get_header(txns, last_block_header, stake, public_key, prestige):
    header = {
        "index": last_block_header["index"] + 1,
        "time": str(datetime.now().time()),
        "nonce": str(int(binascii.hexlify(sha256(
            (public_key + sha256(json.dumps(last_block_header, sort_keys=True).encode('utf8')).hexdigest()).encode(
                'utf8')).hexdigest().encode('utf8')), 16))[:32],
        "prev_hash": sha256(json.dumps(last_block_header, sort_keys=True).encode('utf8')).hexdigest(),
        "stake": stake,
        "miner": public_key,
        "prestige": prestige,
        #     "merkle" : sha256(json.dumps(txns, sort_keys=True).encode('utf8')).hexdigest()  
        "merkle": merkle_root(txns),
        "hash": ""
    }
    header["hash"] = sha256(json.dumps(header, sort_keys=True).encode('utf8')).hexdigest()
    return header

# mine(0, "1EUhfrdDiSnL7bcATvtExQ1PruWMhfwwvV")

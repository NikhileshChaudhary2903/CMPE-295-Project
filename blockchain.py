from flask import Flask, jsonify, request
from urllib.parse import urlparse
from uuid import uuid4

import merkle
import signatures
from hashlib import sha256
import json
import rank_calc


class Blockchain:

    def __init__(self):
        self.chain = [{
            "header": {
                "index": 0,
                "time": 0,
                "nonce": "0",
                "prev_hash": "genesis",
                "stake": 0,
                "prestige": 1,
                "miner": "Nikhilesh Chaudhary, Phani Teja Kantamneni, Arpit Mathur, Arshiya Pathan, Simon Shim",
                "merkle": merkle.merkle_root({})
            },
            "rank": 0,
            "txn": {}
        }]
        self.txn_pool = {}
        self.validated_txn_pool = {}
        self.prestige_pool = {}
        self.nodes = set()
        self.node_identifier = str(uuid4()).replace('-', '')
        self.providers = []

    def get_last_block(self):
        return self.chain[-1]

    def get_txns(self):
        return self.txn_pool

    def get_prestige(self, public_key):
        if public_key in self.prestige_pool:
            return self.prestige_pool[public_key]
        return 0

    def get_providers(self):
        return self.providers

    def add_transaction(self, transaction):
        if signatures.verify_signature(transaction['sender_address'], transaction):
            txn_id = merkle.get_transaction_id(transaction)
            self.txn_pool[txn_id] = transaction
            return len(self.chain), txn_id
        else:
            return -1, 0

    def register_node(self, url):
        parsed_url = urlparse(url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def add_miners_block(self, new_block):
        if new_block["header"]["prev_hash"] == sha256(
                json.dumps(self.chain[-1]["header"], sort_keys=True).encode('utf8')).hexdigest():
            for block_txn in new_block["txn"]:
                self.validated_txn_pool[block_txn] = new_block["txn"][block_txn]
                if block_txn in self.txn_pool:
                    self.txn_pool.pop(block_txn)
            self.chain.append(new_block)

    # returns true if the new_chain is better
    # returns false if self.chain is better
    def find_winning_chain(self, new_chain):
        if len(new_chain) < len(self.chain):
            # self.chain wins on length
            return False
        if len(new_chain) == len(self.chain) and len(self.chain) > 1:
            if json.dumps(new_chain[-1], sort_keys=True).encode('utf8') == json.dumps(self.chain[-1],
                                                                                      sort_keys=True).encode('utf8'):
                return rank_calc.rank_calc(new_chain[-2]["header"], new_chain[-1]["header"]["stake"],
                                           new_chain[-1]["header"]["prestige"]) < rank_calc.rank_calc(
                    self.chain[-2]["header"], self.chain[-1]["header"]["stake"], self.chain[-1]["header"]["prestige"])
        return True



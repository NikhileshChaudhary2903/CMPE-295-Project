from time import time
import json
import hashlib
from flask import Flask,jsonify,request
import datetime

class Blockchain:

    def __init__(self):
        self.chain = []
        self.txn_pool = []

        self.create_block("genesis")

    def create_block(self, prev_hash):
        new_block = {
            "time": time(),
            "header": {
                "index": len(self.chain),
                "root": self.merkle(self.txn_pool),
                "prev_hash": prev_hash if prev_hash != None else self.hash(self.chain[-1]["header"]),
                "nonce": 0
            },
            "txn": self.txn_pool
        }

        self.pow(new_block)

        self.chain.append(new_block)
        self.txn_pool = []

    def merkle(self, txn):
        # print(len(txn))
        if len(txn) == 0:
            return "empty"
        if len(txn) == 1:
            return txn[0]

        next_lvl = []
        if len(txn) % 2 == 1:
            txn.append(txn[-1])
        for i in range(0,len(txn),2):
            next_lvl.append(hash(txn[i:i + 2]))

        return self.merkle(next_lvl)

    def pow(self, block):
        while self.hash(block["header"])[:4] != "0000":
            block["header"]["nonce"] = block["header"]["nonce"] + 1
            block["header"]["index"] = len(self.chain)
            block["header"]["root"] = self.merkle(self.txn_pool)

    def validate_block(self, new_block, sender_ip):
        if new_block["header"]["index"] > len(self.chain):
            self.ask_chain(sender_ip)
        if new_block["header"]["index"] < len(self.chain):
            return self.chain[new_block["header"]["index"]] == new_block
        if self.hash(new_block["header"])[:4] != "0000":
            return False
        if new_block["header"]["prev_hash"] != self.hash(self.chain[-1]["header"]):
            return False
        if new_block["header"]["root"] != self.merkle(new_block["txn"]):
            return False

        self.chain.append(new_block)
        return True

    def validate_chain(self, new_chain, new_txn_pool):
        prev_block = new_chain[0]

        if prev_block["header"]["root"] != self.merkle(prev_block["txn"]):
            return False
        if self.hash(prev_block["header"])[:4] != "0000":
            return False

        for i in range(1, len(new_chain)):
            current_block = new_chain[i]
            prev_block_hash = self.hash(prev_block['header'])
            if prev_block_hash != current_block['header']['prev_hash']:
                return False

            if current_block['header']['root'] != self.merkle(current_block['txn']):
                return False

            if self.hash(current_block['header'])[:4] != "0000":
                return False

            prev_block = current_block

        if len(new_chain) > len(self.chain):
            self.chain = new_chain
            self.txn_pool = new_txn_pool

        return True

    def hash(self, data):
        block_string = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def ask_chain(self, ip):
        pass

    def add_block_to_chain(self):
        pass

    def add_transaction(self,txn):
        self.txn_pool.append(txn)


    def receive_chain(self):







  # Instantiate the Node
app = Flask(__name__)


@app.route('/chain', methods=['GET'])  
def full_blockchain():

    resp={
        'chain': blockchain.chain,
        'host': '0.0.0.0',
        'port': 4000
    }

    return jsonify(resp),201

@app.route('/hello', methods=['GET']) 
def hello():
    return 'Hello World'    

@app.route('/block/<int:blockno>', methods=['GET']) 
def get_block(blockno=None):
    if blockno == None:
        return "Block Not found" , 404

    if len(blockchain.chain) <=  blockno:  
        return "Block Not found" , 404

    else:
        return jsonify(blockchain.chain[blockno]),201



# Instantiate the Blockchain
blockchain = Blockchain()   


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000,debug=True)   
    
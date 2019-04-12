from time import time
import json
import hashlib
from flask import Flask, jsonify, request
import datetime
from urllib.parse import urlparse
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from uuid import uuid4
from collections import OrderedDict

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import binascii

class Blockchain:

    def __init__(self):
        self.chain = []
        self.txn_pool = []
        self.nodes = set()
        self.create_block("genesis")
        self.node_identifier = str(uuid4()).replace('-', '')


    def create_block(self, prev_hash):
        new_block = {
            "time": time(),
            "header": {
                "index": len(self.chain),
                # "root": self.merkle(self.txn_pool),
                "prev_hash": prev_hash if prev_hash != None else self.hash(self.chain[-1]["header"]),
                "nonce": 0
            },
            "txn": self.txn_pool
        }

        self.pow(new_block)

        self.chain.append(new_block)
        self.txn_pool = []
        return new_block 

    ## Sign txn with private key of sender
    def sign_transaction(self,sender_address,sender_private_key,recipient_address,amount):
        """
        Sign transaction with private key
        """
        private_key = RSA.importKey(binascii.unhexlify(sender_private_key))
        signer = PKCS1_v1_5.new(private_key)

        transaction = {'sender_address': sender_address, 
                       'recipient_address': recipient_address,
                       'amount': amount}

        h = SHA.new(str(transaction).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')

    ## Verify txn with public key of sender and signature verification
    def verify_transaction_signature(self, sender_address, signature, transaction):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (sender_address)
        """
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))


    def submit_transaction(self, sender_address, recipient_address, amount, signature):
        """
        Add a transaction to transactions array if the signature is verified
        """
        transaction = {'sender_address': sender_address, 
                        'recipient_address': recipient_address,
                        'amount': amount}
        self.txn_pool.append(transaction)
        return self.get_last_block()['header']['index'] + 1
        # #Reward for mining a block
        # if sender_address == "dummy":
        #     self.txn_pool.append(transaction)
        #     return self.get_last_block()['header']['index'] + 1
        # #Manages txns from wallet to another wallet
        # else:
        #     transaction_verification = self.verify_transaction_signature(sender_address, signature, transaction)
        #     if transaction_verification:
        #         self.txn_pool.append(transaction)
        #         return self.get_last_block()['header']['index'] + 1
        #     else:
        #         return False    


    def register_node(self, url):

        parsed_url = urlparse(url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def merkle(self, txn):
        # print(len(txn))
        if len(txn) == 0:
            return "empty"
        if len(txn) == 1:
            return txn[0]

        next_lvl = []
        if len(txn) % 2 == 1:
            txn.append(txn[-1])
        for i in range(0, len(txn), 2):
            next_lvl.append(hash(txn[i:i + 2]))

        return self.merkle(next_lvl)

    def pow(self, block):
        while self.hash(block["header"])[:4] != "0000":
            block["header"]["nonce"] = block["header"]["nonce"] + 1
            block["header"]["index"] = len(self.chain)
            # block["header"]["root"] = self.merkle(self.txn_pool)

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

    def add_block_to_chain(self,block):
        pass

    def receive_chain(self):
       pass

    def get_last_block(self):
        return self.chain[-1]


# Initialize the Flask app
app = Flask(__name__)

## Generating pub-pvt key pair for Wallets Creation 
## Wont be storing balance in wallet
@app.route('/generate_wallet', methods=['GET'])
def generate_wallet():
    # generate private/public key pair
    key = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)

    d = {}
    d["public_key"] = key.public_key().public_bytes(serialization.Encoding.OpenSSH,
                                                    serialization.PublicFormat.OpenSSH).decode('utf-8')
    d["private_key"] = key.private_bytes(encoding=serialization.Encoding.PEM,
                                         format=serialization.PrivateFormat.TraditionalOpenSSL,
                                         encryption_algorithm=serialization.NoEncryption()).decode('utf-8')

    return jsonify(d), 200

## registering and investigating Nodes
@app.route('/nodes/all', methods=['GET'])
def get_nodes():
    resp = {
        'nodeslist': list(blockchain.nodes),
        'noofnodes': len(blockchain.nodes)
    }
    return jsonify(resp), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    # print(nodes)   
    if nodes is None:
        return "Error: Please enter a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_blockchain():
    resp = {
        'chain': blockchain.chain,
        'host': '0.0.0.0',
        'port': 4000
    }

    return jsonify(resp), 200


@app.route('/hello', methods=['GET'])
def hello():
    return 'Hello World'


@app.route('/block/<int:blockno>', methods=['GET'])
def get_block(blockno=None):
    if blockno == None:
        return "Block Not found", 404

    if len(blockchain.chain) <= blockno:
        return "Block Not found", 404

    else:
        return jsonify(blockchain.chain[blockno]), 200

@app.route('/transactions/new', methods=['POST'])
def add_new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender_address', 'recipient_address', 'amount','signature']
    if not all(k in values for k in required):
        return 'Missing values', 400


    # Create a new Transaction
    index = blockchain.submit_transaction(values['sender_address'], values['recipient_address'], values['amount'],values['signature'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/mine', methods=['GET'])
def mine():

    # We must receive a reward for finding the proof.
    #     # The sender is "dummy" to signify that this node has mined a new coin.
    blockchain.submit_transaction(
        sender_address="Dummy",
        recipient_address=blockchain.node_identifier,
        amount=10,signature=""
    )

    # Forge the new Block by adding it to the chain
    block = blockchain.create_block(prev_hash=None)

    response = {
        'message': "New Block Forged",
        'index': block['header']['index'],
        'transactions': block['txn'],
        'proof': block['header']['nonce'],
        'previous_hash': block['header']['prev_hash'],
    }
    return jsonify(response), 200


@app.route('/gossip', methods=['GET'])
def gossip():
    global blockchain
    data = request.json
    if data["origin"] not in blockchain.nodes:
        blockchain.register_node(data["origin"])
    if data["type"] == "transaction":
        blockchain.submit_transaction(data["data"]["sender_address"], data["data"]["recipient_address"],
                                   data["data"]["amount"])
        return "Sucessfully added transaction", 200
    elif data["type"] == "block":
        blockchain.add_block_to_chain(data["data"]["block"])
        return "Sucessfully added block", 200

    return "Invalid Request", 400

## Generating pub-pvt key pair for Wallets Creation 
## Wont be storing balance in wallet
@app.route('/wallet/create', methods=['GET'])
def reg_new_wallet():
	random_gen = Crypto.Random.new().read
	private_key = RSA.generate(1024, random_gen)
	public_key = private_key.publickey()
	response = {
		'private_key': binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
		'public_key': binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
	}

	return jsonify(response), 200

@app.route('/generate/transaction', methods=['POST'])
def generate_transaction():
	
	sender_address = request.get_json().get('sender_address')
	sender_private_key = request.get_json().get('sender_private_key')
	recipient_address = request.get_json().get('recipient_address')
	amount = request.get_json().get('amount')

	response = {
                        'sender_address': sender_address, 
                        'recipient_address': recipient_address,
                        'amount': amount,
                        'signature': blockchain.sign_transaction(sender_address,sender_private_key,recipient_address,amount)
    }

	return jsonify(response), 200


# Instantiate the Blockchain
blockchain = Blockchain()

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port, debug=True)

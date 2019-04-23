from flask import Flask, jsonify, request
from urllib.parse import urlparse
from uuid import uuid4

import merkle as mer


class Blockchain:

    def __init__(self):
        self.chain = [{
            "header": {
                "index": 0,
                "time": 0,
                "nonce": "0",
                "prev_hash": "genesis",
                "stake": 0,
                "miner": "Nikhilesh Chaudhary, Phani Teja Kantamneni, Arpit Mathur, Arshiya Pathan, Simon Shim",
                "merkle": mer.merkle_root([])
            },
            "rank": 0,
            "txn": []
        }]
        self.txn_pool = []
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
        return len(self.chain)

    def register_node(self, url):
        parsed_url = urlparse(url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


# Initialize the Flask app
app = Flask(__name__)


# registering and investigating Nodes
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
    if blockno is None:
        return "Block Not found", 404

    if len(blockchain.chain) <= blockno:
        return "Block Not found", 404

    else:
        return jsonify(blockchain.chain[blockno]), 200


@app.route('/transactions/new', methods=['POST'])
def add_new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['transaction']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.add_transaction(values['transaction'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/gossip', methods=['GET'])
def gossip():
    global blockchain
    data = request.json
    if data["origin"] not in blockchain.nodes:
        blockchain.register_node(data["origin"])
    if data["type"] == "transaction":
        blockchain.submit_transaction(data["data"]["sender_address"], data["data"]["recipient_address"],
                                      data["data"]["amount"])
        return "Successfully added transaction", 200
    elif data["type"] == "block":
        blockchain.add_block_to_chain(data["data"]["block"])
        return "Successfully added block", 200

    return "Invalid Request", 400


# Instantiate the Blockchain
blockchain = Blockchain()

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port, debug=True)

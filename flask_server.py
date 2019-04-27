from flask import Flask, jsonify, request
from miner import mine
from argparse import ArgumentParser
from threading import Thread
import sys
from ast import literal_eval
from blockchain import Blockchain
# Initialize the Flask app
app = Flask(__name__)

# Instantiate the Blockchain
blockchain = Blockchain.get_instance()
# registering and investigating Nodes

@app.route('/nodes/all', methods=['GET'])
def get_nodes():
    resp = {
        'nodes_list': list(blockchain.nodes),
        'no_of_nodes': len(blockchain.nodes)
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


@app.route('/providers', methods=['GET'])
def get_providers():
    global blockchain
    providers = {
        "providers": blockchain.providers
    }
    return jsonify(providers), 200


@app.route('/provider/add', methods=['POST'])
def add_providers():
    values = request.get_json()
    required = ['ip', 'public_key']
    if not all(k in values for k in required):
        return 'Missing values', 400
    global blockchain
    blockchain.providers.append((values['ip'], values['public_key']))
    response = {'message': 'Provider added'}
    return jsonify(response), 201


@app.route('/block/<int:block_no>', methods=['GET'])
def get_block(block_no=None):
    if block_no is None:
        return "Block Not found", 404

    if len(blockchain.chain) <= block_no:
        return "Block Not found", 404

    else:
        return jsonify(blockchain.chain[block_no]), 200


@app.route('/transaction/add', methods=['POST'])
def add_new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['transaction']
    if not all(k in values for k in required):
        return 'Missing values', 400

    required = ['sender_address']
    if not all(k in values['transaction'] for k in required):
        return 'Missing values', 400

    global blockchain
    index, txn_id = blockchain.add_transaction(values['transaction'])
    if index != -1:
        response = {'message': f'Transaction will be added to Block {index}',
                    'txn_id': txn_id}
        return jsonify(response), 201
    else:
        response = {'message': 'Transaction signature not valid'}
        return jsonify(response), 400


@app.route('/transaction/details', methods=['GET'])
def get_transaction_details():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['txn_id']
    if not all(k in values for k in required):
        return 'Missing values', 400
    global blockchain
    if values['txn_id'] in blockchain.validated_txn_pool:
        response = {'transaction': values['txn_id']}
        return jsonify(response), 201
    else:
        response = {'message': 'Transaction not found'}
        return jsonify(response), 400


@app.route('/gossip', methods=['POST'])
def gossip():
    global blockchain
    data = request.json

    # Check that the required fields are in the POST'ed data
    required = ['origin', 'blockchain', 'transactions']
    if not all(k in data for k in required):
        return 'Missing values', 400

    if data["origin"] not in blockchain.nodes:
        blockchain.register_node(data["origin"])

    for txn in data["transactions"]:
        blockchain.txn_pool[txn] = data["transactions"][txn]

    if blockchain.find_winning_chain(data["blockchain"]):
        blockchain.replace_chain(data["blockchain"])

    return "Gossip Received", 200

def blockchain_run():
    app.run(host='0.0.0.0', port=5000)

def mine_run(stake, pem_file):
    d = {}
    with open(pem_file, 'r') as f:
        d = literal_eval(f.read())
    mine(stake, d["public_key_string"])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-m', '--mine', default=0, type=int, help='1 to mine, 0 to run just the blockchain')
    parser.add_argument('-s', '--stake', default=1, type=int)
    parser.add_argument('-p', '--pem', default=None)
    args = parser.parse_args()
    Thread(target=blockchain_run).start()
    if args.mine == 1:
        stake, pem_file = args.stake, args.pem  
        Thread(target=mine_run, args=(stake, pem_file, )).start()
    
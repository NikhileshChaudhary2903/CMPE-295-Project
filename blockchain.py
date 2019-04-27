from threading import Thread
import merkle
import signatures
from hashlib import sha256
import json
import rank_calc
import copy
from time import sleep
import requests
import binascii


def send_request(blockchain, node):
    try:
        requests.post(node + '/gossip', json={
            'origin': blockchain.node_id,
            'blockchain': blockchain.chain,
            'transactions': blockchain.txn_pool
        })
    except:
        pass


def send_gossip(blockchain):
    while True:
        sleep(0.5)
        for node in blockchain.nodes:
            Thread(target=send_request, args=(blockchain, node)).start()


class Blockchain:
    __instance = None

    @staticmethod
    def get_instance(host="0.0.0.0", port=5000):
        """ Static access method. """
        if Blockchain.__instance is None:
            Blockchain(host, port)
        return Blockchain.__instance

    def __init__(self, host, port):
        if Blockchain.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Blockchain.__instance = self
        self.chain = [{
            "header": {
                "index": 0,
                "time": 0,
                "nonce": "0",
                "prev_hash": "genesis",
                "stake": 0,
                "prestige": 1,
                "miner": "Nikhilesh Chaudhary, Phani Teja Kantamneni, Arpit Mathur, Arshiya Pathan, Simon Shim",
                "merkle": ""
            },
            "rank": 0,
            "txn": {}
        }]
        self.txn_pool = {}
        self.validated_txn_pool = {}
        self.prestige_pool = {}
        self.nodes = set()
        self.providers = []
        self.utxo = {}
        self.node_id = "http://" + host + ":" + str(port)

        txns = [
            {
                "type": -1,
                "receiver": '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxHcvOZ8KbDX2zshqZ1Hu\nZW52w1kGWhZqpkHajH9hv9yzsy872Kq1y4vbpad7q+q6nbP7QCQfru3jnF5xtWFd\n4p+nNro6jVCvTCChGVdzaYT54EO+3t7jn6VC2IADPpU6UnxP1ufehOvCJDZ28Rh5\nGQlE5AQ1NNxkkhEpCk5lTux7l787jPCkalYPcLHveFzE/DfeKWRtLy1KKk9AzEmm\ndr0ca7WLagkkHQIL+SFwRywGvs4iNkebUAtBSQ+WMauEv675FcsrSbwRLvBHd4hB\nInU7asTqPoQkH7hBbnJTWeMhX1fmz3HTMP7lcVz4H8UVIX/GqXS2/xARZQkggy2f\n7QIDAQAB\n-----END PUBLIC KEY-----\n'
            }, {
                "type": -1,
                "receiver": '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxW67N6tcqHSvQK5hSkLX\nk0cxKzilWcXtLUBSksTJkyXasI/HAoCFvqzgyHrjH9EPXL1Z/SUQfZ1nSaaCAncf\nC9ge0irapPI0yW3H1TxUQVZiOVcG+C7ivEyUZDyyHr1GooVSy6HgRtz/R+C97BLe\nV3rLNAjFvl7m0qfd6aZHOzBIMmjm0fAQ9BbkBOKuP/qxv0JW1OT5hP70mbp21Hsr\nuBOqlSH0vB0W2f2cXGqn6SLDuPXtprFnB2T5FGa7erDSnXwGj50vD4crzO2jmtKY\nSGPVibvmhBqwD7ys+zmMduVoi1WTxpUsj2koPCEk/bVKKzQ5g10zf1PSR8ylm06L\n2wIDAQAB\n-----END PUBLIC KEY-----\n'
            }, {
                "type": -1,
                "receiver": '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtHr42GHsCISGKQl3KJW2\niXfpR84R7USxuzDivfK+B44u3263VOP9aelpzhhpdNqqGmv9sEtK+6kai5Q5q6kS\nUsLEdFpUICcu8As8g1CQsVa0YlYwRtoqdp+Pq8SbJ2NMQ0WGFzHnTJPYcgKd1jp/\niMwPqeWxc+BrobwfyZgRh5UT1E/MYjMCY3QOXxlZxh8FdpsSB53lJGJItIXMFVRr\nD92yJsKq5UOPyXieKj7Cbpaaoch0Mhma5+pi+b3FkYNSyaSFadEtcJ1FZenE3k+z\nOPvGSDWB30HuQybnB24amMI7LMUKKryUeRrQE9eqCOaL1cYH8ipdgLBDD1fmiP33\n1QIDAQAB\n-----END PUBLIC KEY-----\n'
            }, {
                "type": -1,
                "receiver": '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwKO8jOygdytZ2UvG6nbl\nQKMte2r9e+mR4ZUJ2wGZIY+1djMx6Veh2o+Ds0hPYbfD3IAl7D8V+6aWkOkNWohk\nvrdSAA/UA57FOInWjGk0pdc5ppTt121bbIs6rE5mUN7Qne5adz+3qM5PT/omok9F\nvD/8/ACH2KByilZnDYMYTzp2NICV/+s14wz+sRfGz2jzCE3mXVKPulqC48MGIZI4\nbT0IfySW3hOn7ImewBKHlHkyziS/ODUVX3NyDtRla+baF+QIxWfl6EGjctU9xPKh\n6xaesv9JjQYtYizSWN6okyifG0DYWgxdd1miM/bdirMqsMKYXlaib4FhajHupHUi\nAwIDAQAB\n-----END PUBLIC KEY-----\n'
            }, {
                "type": -1,
                "receiver": '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyg4sT4Nf9s6p9H636J1T\nDogoOTY67qpjXhejCI1X1fJZHizOsTWROrQFb1CaAelc9ua2Q/hrtoVBz1CaKH4p\n7gU5mOm6dd3msUgVck7uDnG3+i6aQH+PPq5Zu3TCZlZr8IborIJvRUKZQZZFqWt6\n2PbFepf4lnGWyqGikVFlEuN2Ot8IGGHqKZaOQ+KunJ3V5wTrGbdnKDzNn69va0ge\nGidyAo/oD7n4tvqk8pq+h5S5y80OfnF7bwt1P/0XdL1CpKdDxiaT/TctgtsUsybM\n3lq0XxDlbvBFpDnGtNZ6TKmL5WIpLCAQDEX2sJCk2wtGi8esE3vk032dH2IAlNRP\ndQIDAQAB\n-----END PUBLIC KEY-----\n'
            },
            {
                "type": 0,
                "amount": 1000,
                "receiver": '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxHcvOZ8KbDX2zshqZ1Hu\nZW52w1kGWhZqpkHajH9hv9yzsy872Kq1y4vbpad7q+q6nbP7QCQfru3jnF5xtWFd\n4p+nNro6jVCvTCChGVdzaYT54EO+3t7jn6VC2IADPpU6UnxP1ufehOvCJDZ28Rh5\nGQlE5AQ1NNxkkhEpCk5lTux7l787jPCkalYPcLHveFzE/DfeKWRtLy1KKk9AzEmm\ndr0ca7WLagkkHQIL+SFwRywGvs4iNkebUAtBSQ+WMauEv675FcsrSbwRLvBHd4hB\nInU7asTqPoQkH7hBbnJTWeMhX1fmz3HTMP7lcVz4H8UVIX/GqXS2/xARZQkggy2f\n7QIDAQAB\n-----END PUBLIC KEY-----\n'
            }, {
                "type": 0,
                "amount": 1000,
                "receiver": '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxW67N6tcqHSvQK5hSkLX\nk0cxKzilWcXtLUBSksTJkyXasI/HAoCFvqzgyHrjH9EPXL1Z/SUQfZ1nSaaCAncf\nC9ge0irapPI0yW3H1TxUQVZiOVcG+C7ivEyUZDyyHr1GooVSy6HgRtz/R+C97BLe\nV3rLNAjFvl7m0qfd6aZHOzBIMmjm0fAQ9BbkBOKuP/qxv0JW1OT5hP70mbp21Hsr\nuBOqlSH0vB0W2f2cXGqn6SLDuPXtprFnB2T5FGa7erDSnXwGj50vD4crzO2jmtKY\nSGPVibvmhBqwD7ys+zmMduVoi1WTxpUsj2koPCEk/bVKKzQ5g10zf1PSR8ylm06L\n2wIDAQAB\n-----END PUBLIC KEY-----\n'
            }, {
                "type": 0,
                "amount": 1000,
                "receiver": '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtHr42GHsCISGKQl3KJW2\niXfpR84R7USxuzDivfK+B44u3263VOP9aelpzhhpdNqqGmv9sEtK+6kai5Q5q6kS\nUsLEdFpUICcu8As8g1CQsVa0YlYwRtoqdp+Pq8SbJ2NMQ0WGFzHnTJPYcgKd1jp/\niMwPqeWxc+BrobwfyZgRh5UT1E/MYjMCY3QOXxlZxh8FdpsSB53lJGJItIXMFVRr\nD92yJsKq5UOPyXieKj7Cbpaaoch0Mhma5+pi+b3FkYNSyaSFadEtcJ1FZenE3k+z\nOPvGSDWB30HuQybnB24amMI7LMUKKryUeRrQE9eqCOaL1cYH8ipdgLBDD1fmiP33\n1QIDAQAB\n-----END PUBLIC KEY-----\n'
            }, {
                "type": 0,
                "amount": 1000,
                "receiver": '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwKO8jOygdytZ2UvG6nbl\nQKMte2r9e+mR4ZUJ2wGZIY+1djMx6Veh2o+Ds0hPYbfD3IAl7D8V+6aWkOkNWohk\nvrdSAA/UA57FOInWjGk0pdc5ppTt121bbIs6rE5mUN7Qne5adz+3qM5PT/omok9F\nvD/8/ACH2KByilZnDYMYTzp2NICV/+s14wz+sRfGz2jzCE3mXVKPulqC48MGIZI4\nbT0IfySW3hOn7ImewBKHlHkyziS/ODUVX3NyDtRla+baF+QIxWfl6EGjctU9xPKh\n6xaesv9JjQYtYizSWN6okyifG0DYWgxdd1miM/bdirMqsMKYXlaib4FhajHupHUi\nAwIDAQAB\n-----END PUBLIC KEY-----\n'
            }, {
                "type": 0,
                "amount": 1000,
                "receiver": '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyg4sT4Nf9s6p9H636J1T\nDogoOTY67qpjXhejCI1X1fJZHizOsTWROrQFb1CaAelc9ua2Q/hrtoVBz1CaKH4p\n7gU5mOm6dd3msUgVck7uDnG3+i6aQH+PPq5Zu3TCZlZr8IborIJvRUKZQZZFqWt6\n2PbFepf4lnGWyqGikVFlEuN2Ot8IGGHqKZaOQ+KunJ3V5wTrGbdnKDzNn69va0ge\nGidyAo/oD7n4tvqk8pq+h5S5y80OfnF7bwt1P/0XdL1CpKdDxiaT/TctgtsUsybM\n3lq0XxDlbvBFpDnGtNZ6TKmL5WIpLCAQDEX2sJCk2wtGi8esE3vk032dH2IAlNRP\ndQIDAQAB\n-----END PUBLIC KEY-----\n'
            }
        ]
        for txn in txns:
            txn_id = merkle.get_transaction_id(txn)
            self.chain[0]["txn"][txn_id] = txn
            self.validated_txn_pool[txn_id] = txn
            if txn["type"] == -1:
                if txn["receiver"] not in self.prestige_pool:
                    self.prestige_pool[txn["receiver"]] = 0
                self.prestige_pool[txn["receiver"]] += 1
            elif txn["type"] == 0:
                if txn["receiver"] not in self.utxo:
                    self.utxo[txn["receiver"]] = 0
                self.utxo[txn["receiver"]] += txn["amount"]
            if txn["type"] == 1 or txn["type"] == 2:
                if txn["sender"] not in self.utxo:
                    self.utxo[txn["sender"]] = 0
                self.utxo[txn["sender"]] -= txn["amount"]

        self.chain[0]["header"]["merkle"] = merkle.merkle_root(self.validated_txn_pool)

        Thread(target=send_gossip, args=(Blockchain.__instance,)).start()

    def get_last_block(self):
        return copy.deepcopy(self.chain[-1])

    def get_txns(self):
        return copy.deepcopy(self.txn_pool)

    def get_prestige(self, public_key):
        if public_key in self.prestige_pool:
            return copy.deepcopy(self.prestige_pool[public_key])
        return 0

    def get_providers(self):
        return copy.deepcopy(self.providers)

    def add_transaction(self, transaction):
        if signatures.verify_signature(transaction['sender'], transaction):
            if transaction['sender'] not in self.utxo:
                return -2, 0
            if merkle.get_transaction_id(transaction) in self.validated_txn_pool:
                return -3, 0
            if self.utxo[transaction['sender']] >= transaction["amount"]:
                txn_id = merkle.get_transaction_id(transaction)
                self.txn_pool[txn_id] = transaction
                return len(self.chain), txn_id
            else:
                return -2, self.utxo[transaction['sender']]
        return -1, 0

    def register_node(self, url):
        self.nodes.add(url)

    def add_miners_block(self, new_block):
        if new_block["header"]["prev_hash"] == sha256(
                json.dumps(self.chain[-1]["header"], sort_keys=True).encode('utf8')).hexdigest():
            for block_txn_id in new_block["txn"]:
                block_txn = new_block["txn"][block_txn_id]
                self.validated_txn_pool[block_txn_id] = block_txn
                if block_txn_id in self.txn_pool:
                    self.txn_pool.pop(block_txn_id)
                if block_txn["type"] == -1:
                    if block_txn["receiver"] not in self.prestige_pool:
                        self.prestige_pool[block_txn["receiver"]] = 0
                    self.prestige_pool[block_txn["receiver"]] += 1
                if block_txn["type"] == 0 or block_txn["type"] == 1 or block_txn["type"] == 2:
                    if block_txn["receiver"] not in self.utxo:
                        self.utxo[block_txn["receiver"]] = 0
                    self.utxo[block_txn["receiver"]] += block_txn["amount"]
                if block_txn["type"] == 1 or block_txn["type"] == 2:
                    if block_txn["sender"] not in self.utxo:
                        self.utxo[block_txn["sender"]] = 0
                    self.utxo[block_txn["sender"]] -= block_txn["amount"]

            self.chain.append(new_block)

    # returns true if the new_chain is better
    # returns false if self.chain is better
    def find_winning_chain(self, new_chain):
        if len(new_chain) < len(self.chain):
            # self.chain wins on length
            return False
        if len(new_chain) == len(self.chain) and len(self.chain) > 1:
            if json.dumps(new_chain[-2], sort_keys=True).encode('utf8') == json.dumps(self.chain[-2],
                                                                                      sort_keys=True).encode('utf8'):
                return rank_calc.rank_calc(new_chain[-2]["header"], new_chain[-1]["header"]["stake"],
                                           new_chain[-1]["header"]["prestige"],
                                           new_chain[-1]["header"]["miner"]) < rank_calc.rank_calc(
                    self.chain[-2]["header"], self.chain[-1]["header"]["stake"], self.chain[-1]["header"]["prestige"],
                    self.chain[-1]["header"]["miner"])
        return True

    @staticmethod
    def validate_chain(chain):
        prev_block = {
            "header": "genesis"
        }
        for i, block in enumerate(chain):
            if merkle.merkle_root(block["txn"]) != block["header"]["merkle"]:
                return False, "Error in merkle root at block " + str(i)
            if i > 0 and block["header"]["prev_hash"] != sha256(
                    json.dumps(prev_block["header"], sort_keys=True).encode('utf8')).hexdigest():
                return False, "Error in previous hash at block " + str(i)
            if i > 0 and block["header"]["nonce"] != str(int(binascii.hexlify(sha256((block["header"]["miner"] + sha256(
                    json.dumps(prev_block["header"], sort_keys=True).encode('utf8')).hexdigest()).encode(
                'utf8')).hexdigest().encode('utf8')), 16))[:32]:
                return False, "Error in nonce at block " + str(i)
            prev_block = block
        return True, "All good"

    def replace_chain(self, new_chain):
        utxo = {}
        txn_pool = copy.deepcopy(self.txn_pool)
        txn_pool.update(copy.deepcopy(self.validated_txn_pool))
        validated_txn_pool = {}
        prestige_pool = {}
        for new_block in new_chain:
            for block_txn_id in new_block["txn"]:

                block_txn = new_block["txn"][block_txn_id]
                validated_txn_pool[block_txn_id] = block_txn
                if block_txn_id in txn_pool:
                    txn_pool.pop(block_txn_id)

                if block_txn["type"] == -1:
                    if block_txn["receiver"] not in prestige_pool:
                        prestige_pool[block_txn["receiver"]] = 0
                    prestige_pool[block_txn["receiver"]] += 1

                if block_txn["type"] == 0 or block_txn["type"] == 1 or block_txn["type"] == 2:
                    if block_txn["receiver"] not in utxo:
                        utxo[block_txn["receiver"]] = 0
                    utxo[block_txn["receiver"]] += block_txn["amount"]
                if block_txn["type"] == 1 or block_txn["type"] == 2:
                    if block_txn["sender"] not in utxo:
                        utxo[block_txn["sender"]] = 0
                    utxo[block_txn["sender"]] -= block_txn["amount"]
        self.chain = new_chain
        self.txn_pool = txn_pool
        self.validated_txn_pool = validated_txn_pool
        self.prestige_pool = prestige_pool
        self.utxo = utxo

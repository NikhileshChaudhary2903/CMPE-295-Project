
import json

class Blockchain():

    def get_last_block(self):
        return {
            "header" : {
                "index" : 1,
                "time" : 1234,
                "nonce" : '34298789789308475128743123847134906324851237482374089723847123857832476508237468923745',
                "prev_hash" : "akefu3j24kj234",
                "stake" : 4352,
                "miner" : "akefu3j24kj234",
                "merkle" : "akefu3j24kj234"
            },

            "txn": [
                {
                    "type" : 1,
                    "sender": "publickey0",
                    "amount": 909,
                    "receiver": "publickey12",
                }
            ]
        }

    def get_txns(self):          # return just the list of un-mined transactions
        return  [
                {
                    "type" : 1,
                    "sender": "publickey2",
                    "amount": 909,
                    "receiver": "publickey5",
                }
            ]

    def get_prestige(self):
        return 10;

    def get_providers(self):
        return [("ip", "public_key")]

    def send_transaction(self, txn):     # txn = { "type" : 2,
                                    #       "sender" : "sender_address",
                                    #       "receiver" : "receiver_address",
                                    #       "amount" : 1,
                                    #       "chunk_hash" : "hash_of_the_file_chunk"
                                    #       }
        return "transaction_id"



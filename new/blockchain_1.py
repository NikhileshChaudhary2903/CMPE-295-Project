

def get_last_block():
    return {
        "header" : {
            "index" : 1,
            "time" : 1234,
            "nonce" : 342.98789789,
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


def get_txn():
    return {
        "merkel" : "jhbhjbhjbhj",
        "data" : [
            
            {
                "type" : 1,
                "sender": "publickey2",
                "amount": 909,
                "receiver": "publickey5",
            }
        ]
    }

    def merkel_root(my_transactions):
        block_string = json.dumps(my_transactions, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


def get_prestige():
    return 10;



def get_providers():
    return [("ip", "public_key")]

def send_transaction(txn):     # txn = { "type" : 2,
                                #       "sender" : "sender_address",
                                #       "receiver" : "receiver_address",
                                #       "amount" : 1,
                                #       "chunk_hash" : "hash_of_the_file_chunk"
                                #       }
    return "transaction_id"



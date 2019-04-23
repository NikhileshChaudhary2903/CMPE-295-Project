import signatures
import requests
import os
import sys
import wallets

def upload_file(file_name, full_node, public_key=None, private_key=None):
    if public_key is None:
        d = wallets.get_wallet()
        public_key = d["public_key"]
        private_key = d["private_key"]
    
    create_transaction()    


def create_transaction():
    pass


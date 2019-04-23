import signatures
import requests
import os
import sys
import wallets
from pathlib import Path
from hashlib import sha256
from random import choice
def upload_file(file_name, full_node_ip, public_key=None, private_key=None):
    if public_key is None:
        d = wallets.get_wallet()
        public_key = d["public_key_string"]
        private_key = d["private_key_string"]
    # file_size = os.path.getsize(str(Path(file_name).resolve()))
    file_chunk_size = 1024 * 1024 * 10
    file_details = []
    chunk_id = 0
    
    with open(file_name, "rb") as f:
        for seq in iter(lambda: f.read(file_chunk_size), b""):
            file_details.append({'name' : file_name + '_' + str(chunk_id), 'hash' : sha256(seq).hexdigest(), 'size' : file_chunk_size})
            chunk_id += 1

    file_hashes = []
    providers_list = requests.get(full_node_ip+'/get_providers')
    for file_detail in file_details:
        provider = choice(providers_list['providers'])
        provider_public_key = provider[1]
        file_hashes.append(create_transaction(public_key, provider_public_key, file_detail))

def create_transaction(sender_address, receiver_address, file):
    pass
    

upload_file("admit.pdf", "0.0.0.0:5000")
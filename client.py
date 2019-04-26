import signatures
import requests
import os
import sys
import wallets
from pathlib import Path
from hashlib import sha256
from random import choice
from time import sleep
import transfer_pb2
import transfer_pb2_grpc
import grpc
from ast import literal_eval
from datetime import datetime

full_node_ip = 'http://0.0.0.0:5000'

def upload_file(file_name, public_key=None, private_key=None):
    if public_key == "":
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
            with open('tmp_uploads/' + file_details[-1]['name'], 'wb') as part:
                part.write(seq)
            chunk_id += 1

    # file_txn_ids = []
    providers_list = requests.get(full_node_ip+'/providers').json()
    rand_provider_list = []
    for file_detail in file_details:
        provider = choice(providers_list['providers'])
        rand_provider_list.append(provider)
        provider_public_key = provider[1]
        # file_txn_ids.append(file_txn_id)
        file_txn_id = create_transaction(public_key, private_key, provider_public_key, 0, file_detail)
        file_detail['txn_id'] = file_txn_id
    
    with open(file_name + '.txt', "w") as f:
        f.write(str(file_details))
    # Wait till the trasactions are mined into a block
    # print(rand_provider_list)
    sleep(2)
 
    for i in range(len(file_details)):
        call_upload(file_details[i], rand_provider_list[i])
    
    print('Done...')
 # Write gRPC calls here   
def call_upload(file_details, provider):
    seq_list = []
    with open('tmp_uploads/' + file_details['name'], "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            seq_list.append(transfer_pb2.FileData(fileName=file_details['name'], fileHash=str(file_details['hash']), txnId=file_details['txn_id'], data=chunk))

        provider_stub = transfer_pb2_grpc.fileTransferStub(grpc.insecure_channel('localhost:5001'))
        # print(provider_stub)
        provider_stub.UploadFile(gen_stream(seq_list), timeout=2)
    

def gen_stream(list_of_chunks):
    for chunk in list_of_chunks:
        yield chunk        

def create_transaction(sender_address, sender_private_key, receiver_address, amount, file_details):
    txn = {"type" : 2,
            "sender_address" : sender_address,
            "amount" : amount,
            "receiver_address" : receiver_address, 
            "file" : file_details }

    signed_txn = signatures.sign_data(sender_private_key, txn)
    signed_txn_id = requests.post(full_node_ip+'/transaction/add', json={'transaction':signed_txn}).json()
    print(signed_txn_id)
    return signed_txn_id['txn_id']

def download_file(file_name, private_key):
    file_details = []
    with open(file_name + '.txt', 'r') as f:
        file_details = literal_eval(f.read())
    
    with open(file_name, 'wb') as f:
        for file_detail in file_details:
            txn_details = requests.post(full_node_ip + '/transaction/details', data={'txn_id' : file_detail['txn_id']})
            provider_ip = txn_details['receiver_address']
            signed_time = signatures.sign_data(private_key, {'time' : str(datetime.now().time())})
            provider_stub = transfer_pb2_grpc.fileTransferStub(grpc.insecure_channel(provider_ip))
            try:
                file_data_iterator = provider_stub.DownloadFile(transfer_pb2.FileInfo(fileName=file_detail['name'], txnid=file_detail['txn_id'], signedTime=signed_time), timeout=1)
            except TimeoutError:
                print('File Transfer Failed')
                sys.exit(1)
            for resp in file_data_iterator:
                f.write(resp.data)
    print('Done...')    

if __name__ == "__main__":
    try:
        cmd, file_name, public_key, private_key = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    except IndexError:
        print("Need 4 command line arguments, please try again...")
        sys.exit(1)
    if cmd.lower() == 'download':
        download_file(file_name, private_key)
    elif cmd.lower() == 'upload':
        upload_file(file_name, public_key, private_key)
    else:
        print("Wrong command line argument, please try again...")
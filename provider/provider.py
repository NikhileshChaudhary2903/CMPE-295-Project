import sys
import os
from pathlib import Path
sys.path.append(str(Path(os.path.dirname(os.path.abspath(__file__))).parent)+'/proto')
sys.path.append(str(Path(os.path.dirname(os.path.abspath(__file__))).parent)+'/wallets')
sys.path.append(str(Path(os.path.dirname(os.path.abspath(__file__))).parent)+'/signatures')
import grpc
from concurrent import futures
from time import sleep
import requests
from datetime import datetime
from ast import literal_eval
import signatures
import wallets
from flask import jsonify
from argparse import ArgumentParser
import transfer_pb2
import transfer_pb2_grpc
import json

with open('../conf/config.json', 'r') as conf:
    config = json.load(conf)

full_node_ip = config["full_node_ip"]
my_ip = config["provider_ip"]

DOWNLOAD_DIR = str(os.path.dirname(os.path.abspath(__file__))) + '/files/'
if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class FileTransfer(transfer_pb2_grpc.fileTransferServicer):
    def UploadFile(self, fileDataStream, context):
        fd = fileDataStream.next()
        file_name = fd.fileName
        file_hash = fd.fileHash
        txn_id = fd.txnId
        resp = requests.get(full_node_ip+'/transaction/details', json={'txn_id' : txn_id})
        # print(resp.json())
        if resp.status_code == 201:
            resp = resp.json()
            amount = resp['transaction']['amount']
            with open(DOWNLOAD_DIR + file_hash + '_' + file_name, "wb") as f:
                f.write(fd.data)
                for seq in fileDataStream:
                    f.write(seq.data)
            file_read_details = {file_hash + '_' + file_name : {'reads_left' : [[int(amount * 1000), (str(datetime.now().time()), {"time" : str(datetime.now().time()), "signature" : ""})]]}}
            with open(DOWNLOAD_DIR + file_hash + '_' + file_name + '.txt', "w") as f:
                f.write(str(file_read_details))
            return transfer_pb2.FileInfo(fileName=file_name, errMess="")
        return transfer_pb2.FileInfo(errMess="Transfer Failed")
    
    def DownloadFile(self, fileInfo, context):
        file_name = fileInfo.fileName
        txn_id = fileInfo.txnId
        signed_time = dict(fileInfo.signedTime)
        txn_details = requests.get(full_node_ip + '/transaction/details', json={'txn_id' : txn_id}).json()['transaction']
        sender_public_key = txn_details['sender']
        
        if signatures.verify_signature(sender_public_key, signed_time):
            file_hash = txn_details['file']['hash']
            file_read_details = {}
            
            with open(DOWNLOAD_DIR + file_hash + '_' + file_name + '.txt', 'r') as f:
                file_read_details = literal_eval(f.read())
            tmp_tup = file_read_details[file_hash + '_' + file_name]['reads_left'][-1] 
            reads_left = tmp_tup[0] - 1
            time_read = (str(datetime.now().time()), signed_time)
            file_read_details[file_hash + '_' + file_name]['reads_left'].append([reads_left, time_read])
            
            with open(DOWNLOAD_DIR + file_hash + '_' + file_name + '.txt', 'w') as f:
                f.write(str(file_read_details))
            
            with open(DOWNLOAD_DIR + file_hash + '_' + file_name, "rb") as f:
                for chunk in iter(lambda: f.read(1024*1024 * 10), b""):
                    yield transfer_pb2.FileData(fileName=file_name, fileHash=file_hash, txnId=txn_id, data=chunk, errMess="ok")  
        else:
            yield transfer_pb2.FileData(errMess="Signature Verification Failed")

def serve(pem_file="", port=6000):
    d = {}
    public_key = ""
    private_key = ""
    if pem_file is "":
        wallets.generate_pem()
        with open('private_key.pem', 'r') as f:
            d = literal_eval(f.read())
        public_key, private_key = d['public_key_string'], d['private_key_string']
    else:
        with open(pem_file, 'r') as f:
            d = literal_eval(f.read())
        public_key, private_key = d['public_key_string'], d['private_key_string']
    
    resp = requests.post(url = full_node_ip+'/provider/add', json={'ip' : my_ip, 'public_key' : public_key})
    if resp.status_code == 400:
        print("Couldn't register provider, please try again...")
        sys.exit(1)
    # print(resp.json())
    file_transfer = FileTransfer()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    transfer_pb2_grpc.add_fileTransferServicer_to_server(file_transfer, server)
    server.add_insecure_port(my_ip[7:])
    server.start()
    print("Provider Listening on ", my_ip)
    try:
        while True:
            sleep(86400)
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=6000, type=int)
    parser.add_argument('-pe', '--pem', default="", type=str)
    args = parser.parse_args()
    serve('../pem/' + args.pem, args.port)
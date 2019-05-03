import sys
import os
from pathlib import Path
sys.path.append(str(Path(os.path.dirname(os.path.abspath(__file__))).parent)+'/proto')
sys.path.append(str(Path(os.path.dirname(os.path.abspath(__file__))).parent)+'/wallets')
sys.path.append(str(Path(os.path.dirname(os.path.abspath(__file__))).parent)+'/signatures')
import signatures
import requests
import wallets
from hashlib import sha256
from random import choice
from time import sleep
import transfer_pb2
import transfer_pb2_grpc
import grpc
from ast import literal_eval
from datetime import datetime
from argparse import ArgumentParser

# full_node_ip = 'http://169.254.42.254:5000'
full_node_ip = 'http://0.0.0.0:5000'
UPLOADS_DIR = str(os.path.dirname(os.path.abspath(__file__))) + '/uploads/'
DOWNLOAD_DIR = str(os.path.dirname(os.path.abspath(__file__))) + '/downloads/'

chunk_to_amount = { 10 : 10.0, 32 : 15.0, 64 : 30.0, 128 : 50.0, 256 : 100.0, 512 : 150.0, 1024 : 200.0 }

def upload_file(file_name, pem_file="", chunk_size=10):
    public_key = ""
    private_key = ""
    if pem_file is "":
        wallets.generate_pem()
        d = {}
        with open('private_key.pem', 'r') as f:
            d = literal_eval(f.read())
        public_key = d["public_key_string"]
        private_key = d["private_key_string"]
    else:
        d = {}
        with open(pem_file, 'r') as f:
            d = literal_eval(f.read())
        public_key = d["public_key_string"]
        private_key = d["private_key_string"]

    file_chunk_size = 1024 * 1024 * chunk_size
    file_details = []
    chunk_id = 0
    
    with open(UPLOADS_DIR + file_name, "rb") as f:
        for seq in iter(lambda: f.read(file_chunk_size), b""):
            file_details.append({'name' : file_name + '_' + str(chunk_id), 'hash' : sha256(seq).hexdigest(), 'size' : file_chunk_size})
            with open('tmp_uploads/' + file_details[-1]['name'], 'wb') as part:
                part.write(seq)
            chunk_id += 1

    # file_txn_ids = []
    providers_list = requests.get(full_node_ip+'/providers').json()
    if providers_list['providers'] == []:
        print("No provider available, try again later...")
        sys.exit(1)
    rand_provider_list = []
    for file_detail in file_details:
        provider = choice(providers_list['providers'])
        rand_provider_list.append(provider)
        provider_public_key = provider[1]
        # file_txn_ids.append(file_txn_id)
        file_txn_id = create_transaction(2, public_key, private_key, provider_public_key, chunk_to_amount[chunk_size], file_detail)
        file_detail['txn_id'] = file_txn_id
        file_detail['provider_ip'] = provider[0]
    
    with open(UPLOADS_DIR + file_name + '.txt', "w") as f:
        f.write(str(file_details))

    # Wait till the trasactions are mined into a block
    sleep(30)
    
    try:
        for i in range(len(file_details)):
            call_upload(file_details[i], rand_provider_list[i])
    except Exception as e:
        return "File Upload failed : " + str(e)
        
    
    return "File Uploaded"

 # Write gRPC calls here   
def call_upload(file_details, provider):
    seq_list = []
    with open('tmp_uploads/' + file_details['name'], "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            seq_list.append(transfer_pb2.FileData(fileName=file_details['name'], fileHash=str(file_details['hash']), txnId=file_details['txn_id'], data=chunk))

        provider_stub = transfer_pb2_grpc.fileTransferStub(grpc.insecure_channel(provider[0][7:]))
        # print(provider_stub)
        try:
            file_info = provider_stub.UploadFile(gen_stream(seq_list), timeout=2)
            if file_info.errMess == "Transfer Failed":
                print("Transfer failed")
                sys.exit(1)
        except Exception as e:
            print("Error occurred while file transfer : ", e)
    
    
# generate a stream of chunks for a given file
def gen_stream(list_of_chunks):
    for chunk in list_of_chunks:
        yield chunk        

def create_transaction(type, sender_address, sender_private_key, receiver_address, amount, file_details):
    if type == 2:
        txn = {"type" : type,
                "sender" : sender_address,
                "amount" : amount,
                "receiver" : receiver_address,
                "time":str(datetime.now().time()), 
                "file" : file_details }
    elif type == 1:
        txn = {"type" : type,
                "sender" : sender_address,
                "amount" : amount,
                "receiver" : receiver_address,
                "time" : str(datetime.now().time()) }
    else:
        print("Wrong transaction type specified, please try again...")
        sys.exit(1)

    signed_txn = signatures.sign_data(sender_private_key, txn)
    signed_txn_id = requests.post(full_node_ip+'/transaction/add', json={'transaction':signed_txn}).json()
    print(signed_txn_id)
    return signed_txn_id['txn_id']

def download_file(file_name, pem_file=None):
    # public_key = ""
    private_key = ""
    if pem_file is None or pem_file is "":
        wallets.generate_pem()
        d = {}
        with open('private_key.pem', 'r') as f:
            d = literal_eval(f.read())
        # public_key = d["public_key_string"]
        private_key = d["private_key_string"]
    else:
        d = {}
        with open(pem_file, 'r') as f:
            d = literal_eval(f.read())
        # public_key = d["public_key_string"]
        private_key = d["private_key_string"]
    file_details = []
    with open(UPLOADS_DIR + file_name + '.txt', 'r') as f:
        file_details = literal_eval(f.read())
    
    with open(DOWNLOAD_DIR + file_name, 'wb') as f:
        for file_detail in file_details:
            txn_details = requests.get(full_node_ip + '/transaction/details', json={'txn_id' : file_detail['txn_id']}).json()['transaction']
            provider_ip = file_detail['provider_ip']
            print(provider_ip)
            signed_time = signatures.sign_data(private_key, {'time' : str(datetime.now().time())})
            provider_stub = transfer_pb2_grpc.fileTransferStub(grpc.insecure_channel(provider_ip[7:]))
            try:
                file_data_iterator = provider_stub.DownloadFile(transfer_pb2.FileInfo(fileName=file_detail['name'], txnId=file_detail['txn_id'], signedTime=signed_time))
            except:
                print('File Transfer Failed')
                sys.exit(1)
            for resp in file_data_iterator:
                if resp.errMess == "ok":
                    f.write(resp.data)
                else:
                    print("Signature Verification Failed")
                    sys.exit(1)
    print('Done...')    

def send_money(receiver_public_key, amount, pem_file):
    sender_public_key = ""
    sender_private_key = ""
    if pem_file is "":
        wallets.generate_pem()
        d = {}
        with open('private_key.pem', 'r') as f:
            d = literal_eval(f.read())
        sender_public_key = d["public_key_string"]
        sender_private_key = d["private_key_string"]
    else:
        d = {}
        with open(pem_file, 'r') as f:
            d = literal_eval(f.read())
        sender_public_key = d["public_key_string"]
        sender_private_key = d["private_key_string"]

    return create_transaction(1, sender_public_key, sender_private_key, receiver_public_key, amount, {})

def secure_share(file_name, pem_file=""):
    public_key = ""
    private_key = ""
    if pem_file is "":
        wallets.generate_pem()
        tmp = {}
        with open('private_key.pem', 'r') as f:
            tmp = literal_eval(f.read())
        public_key = tmp["public_key_string"]
        private_key = tmp["private_key_string"]
    else:
        tmp = {}
        with open(pem_file, 'r') as f:
            tmp = literal_eval(f.read())
        public_key = tmp["public_key_string"]
        private_key = tmp["private_key_string"]
    
    file_details = []
    with open(file_name + '.txt', 'r') as f:
        file_details = literal_eval(f.read())

    for file_detail in file_details:
        file_detail['signed_time'] = signatures.sign_data(private_key, {'time' : str(datetime.now().time())})

    return file_details


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-c', '--cmd', default="", type=str)
    parser.add_argument('-f', '--file', default="", type=str)
    parser.add_argument('-p', '--pem', default="", type=str)
    parser.add_argument('-pb', '--publickey', default="", type=str)
    parser.add_argument('-a', '--amount', default=0.0, type=float)
    parser.add_argument('-csz', '--chunksize', default=10, type=int)
    args = parser.parse_args()

    if args.cmd.lower() == "send":
        receiver = args.publickey
        pem_file = '../pem/' + args.pem
        amount = float(args.amount)
        print("transaction_id : ", send_money(receiver, amount, pem_file))
    elif args.cmd.lower() == "download":
        pem_file = '../pem/' + args.pem
        file_name = args.file
        download_file(file_name, pem_file)
    elif args.cmd.lower() == "upload":
        pem_file = '../pem/' + args.pem
        file_name = args.file
        chunk_size = args.chunksize
        upload_file(file_name, pem_file, chunk_size) # enter chunksize in MB based on the amount willing to spend
    # elif args.cmd.lower() == "secure_share":
    #     pem_file = args.pem
    #     file_name = args.file
    #     secure_share(file_name, pem_file)
    else:
        print("Please enter valid command...")
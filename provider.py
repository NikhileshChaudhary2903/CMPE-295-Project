import transfer_pb2
import transfer_pb2_grpc
import grpc
from concurrent import futures
from time import sleep
import sys
import requests
from datetime import datetime
from ast import literal_eval
import signatures

full_node_ip = "0.0.0.0:5000"
my_ip = '0.0.0.0:5001'

class FileTransfer(transfer_pb2_grpc.fileTransferServicer):
    def UploadFile(self, fileDataStream, context):
        fd = fileDataStream.next()
        file_name = fd.fileName
        file_hash = fd.file_hash
        txn_id = fd.txnId
        resp = requests.post(full_node_ip+'/trasaction/details', data={'txn_id' : txn_id})
        # TODO verify whether the trasaction is valid
        if resp.status_code == 200:
            with open(file_hash + '_' + file_name, "wb") as f:
                f.write(fd.data)
                for seq in fileDataStream:
                    f.write(seq.data)
            file_read_details = {file_hash + '_' + file_name : {'reads_left' : [(500, (str(datetime.now().time()), 0))]}}
            with open(file_hash + '_' + file_name + '.txt', "w") as f:
                f.write(str(file_read_details))
            return transfer_pb2.FileInfo(fileName=file_name)
    
    def DownloadFile(self, fileInfo, context):
        file_name = fileInfo.fileName
        txn_id = fileInfo.txnId
        signed_time = dict(fileInfo.signedTime)
        txn_details = requests.post(full_node_ip + '/transaction/details', data={'txn_id' : txn_id})
        sender_public_key = txn_details['sender_address']
        if signatures.verify_signature(sender_public_key, signed_time):
            file_hash = txn_details['file']['hash']
            file_read_details = {}
            with open(file_hash + '_' + file_name + '.txt', 'r') as f:
                file_read_details = literal_eval(f.read())
            tmp_tup = file_read_details[file_hash + '_' + file_name]['reads_left'][-1] 
            reads_left = tmp_tup[0] - 1
            time_read = (str(datetime.now().time()), signed_time)
            file_read_details[file_hash + '_' + file_name]['reads_left'].append((reads_left, time_read))
            with open(file_hash + '_' + file_name + '.txt', 'w') as f:
                f.write(str(file_read_details))
            
            with open(file_hash + '_' + file_name, "rb") as f:
                for chunk in iter(lambda: f.read(1024*1024 * 10), b""):
                    yield transfer_pb2.FileData(fileName=file_name, fileHash=file_hash, txnId=txn_id, data=chunk)  

def serve(ip):
    try:
        public_key, private_key = sys.argv[1], argv[2]
    except IndexError:
        print("Need 2 command line arguments, please try again...")
        sys.exit(1)
    resp = requests.post(full_node_ip+'/provider/add', data={'ip' : my_ip, 'public_key' : public_key})
    if resp.status_code == 400:
        print("Couldn't register provider, please try again...")
        sys.exit(1)
    file_transfer = FileTransfer()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    transfer_pb2_grpc.add_fileTransferServicer_to_server(file_transfer, server)
    server.add_insecure_port(ip)
    server.start()

    try:
        while True:
            sleep(86400)
    except KeyboardInterrupt:
        sys.exit(1)


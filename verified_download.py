from client import secure_share
from argparse import ArgumentParser
import grpc
import transfer_pb2
import transfer_pb2_grpc
import sys

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-f', '--file', default="", type=str)
    parser.add_argument('-p', '--pem', default="", type=str)

    args = parser.parse_args()
    file_details = secure_share(args.file, args.pem)
    with open(file_details[0]['name'].rsplit('_')[0], 'wb') as f:
        for file_detail in file_details:
            provider_stub = transfer_pb2_grpc.fileTransferStub(grpc.insecure_channel(file_detail['provider_ip'][7:]))
            file_data_stream = provider_stub.DownloadFile(transfer_pb2.FileInfo(fileName=file_detail['name'], txnId=file_detail['txn_id'], signedTime=file_detail['signed_time']))
            fds =  file_data_stream.next()
            if fds.errMess == "ok":
                f.write(fds.data)
                for fd in file_data_stream:
                    f.write(fd.data)
            else:
                print("Signature Verification Failed")
                sys.exit(1)

    print("Done...")
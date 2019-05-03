import client
from argparse import ArgumentParser
import sys

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-f', '--file', default="", type=str)
    parser.add_argument('-p', '--pem', default="", type=str)

    args = parser.parse_args()
    file_details = client.secure_share(args.file, args.pem)
    print(file_details)
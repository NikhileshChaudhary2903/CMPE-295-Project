import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

class Blockchain:

    def __init__(self):
        self.chain=[]
        self.txn_pool=[]

    def create_block():
        newBolck = {
            header: {
                index : len(self.chain),
                time : time(),
                root : self.merkel(txn_pool),
                prev_hash : self.hash(self.chain[-1]["header"]),
                nonce : 0
            },
            txn : selftxn_pool
        }

        pow(newBolck)

        self.chain.append(b)

    def merkel():

    def validate_block():


    def validate_chain():



    def hash():



    def add_block_to_chain():





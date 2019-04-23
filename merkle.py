from hashlib import sha256
import codecs
import json

def merkle_root(txns):
    transactions = []
    for txn in txns:
        transactions.append(sha256(json.dumps(txn, sort_keys=True).encode('utf8')).hexdigest())
    return str(merkle(transactions))[2:-1]

def merkle(hashList):
    if len(hashList) == 1:
        return hashList[0]
    newHashList = []
    # Process pairs. For odd length, the last is skipped
    for i in range(0, len(hashList)-1, 2):
        newHashList.append(hash2(hashList[i], hashList[i+1]))
    if len(hashList) % 2 == 1: # odd, hash last item twice
        newHashList.append(hash2(hashList[-1], hashList[-1]))
    return merkle(newHashList)
 
def hash2(a, b):
    # Reverse inputs before and after hashing
    # due to big-endian / little-endian nonsense
    a1 = codecs.decode(a, 'hex')
    a11 = a1[::-1]
    # print a11.encode('hex')
    b1 = codecs.decode(b, 'hex')[::-1]
    #print b1.encode('hex')
    concat = a11+b1
    #print concat.encode('hex')
    concat2 = sha256(concat).digest()
    # print ("hash1:" + str(codecs.encode(concat2, 'hex')))
    h = sha256(concat2).digest()
    # print ("hash2:" + str(codecs.encode(h[::-1], 'hex')))
    # print (" ")
    return codecs.encode(h[::-1], 'hex')

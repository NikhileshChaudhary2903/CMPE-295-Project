from hashlib import sha256
import codecs
import json


def merkle_root(txns):
    return sha256(json.dumps(txns, sort_keys=True).encode('utf8')).hexdigest()

def merkle(hash_list):
    if len(hash_list) == 0:
        return ""
    if len(hash_list) == 1:
        return hash_list[0]
    new_hash_list = []
    # Process pairs. For odd length, the last is skipped
    for i in range(0, len(hash_list) - 1, 2):
        new_hash_list.append(hash2(hash_list[i], hash_list[i + 1]))
    if len(hash_list) % 2 == 1:  # odd, hash last item twice
        new_hash_list.append(hash2(hash_list[-1], hash_list[-1]))
    return merkle(new_hash_list)


def hash2(a, b):
    # Reverse inputs before and after hashing
    # due to big-endian / little-endian nonsense
    a1 = codecs.decode(a, 'hex')
    a11 = a1[::-1]
    # print a11.encode('hex')
    b1 = codecs.decode(b, 'hex')[::-1]
    # print b1.encode('hex')
    concat = a11 + b1
    # print concat.encode('hex')
    concat2 = sha256(concat).digest()
    # print ("hash1:" + str(codecs.encode(concat2, 'hex')))
    h = sha256(concat2).digest()
    # print ("hash2:" + str(codecs.encode(h[::-1], 'hex')))
    # print (" ")
    return codecs.encode(h[::-1], 'hex')

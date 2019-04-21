from hashlib import sha256
import codecs

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

txHashes = [
"338bbd00b893c384eb2b11e70f3875447297c5f20815499e787867df4538e48d",
"1ad1138c6064dd17d0a4d12016d629c18f15fc9d1472412945f9c91a696689c7",
"c77834d14d66729014b06fcf45c5f82af4bdd9d816e787f01bfa525cfa147014",
"bb3d83398d7517fe643b2421d795e73c342b6a478ef53acdaab35dbdffbbcdb5",
"38d563caf0e9ed103515cab09e40e49da0ccb8c0765ce304f9556e5bc62e8ff5",
"8fc0507359d0122fa14b5887034d857bd69c8bc0e74c8dd428c2fc098595c285",
"9db9fe6d011c1c7e997418aeec78ccb659648cfc915b2ff1154cabb41359ac70",
"3c72fdb7e38e4437faa9e5789df6b51505de014b062361ef47578244d5025628"
]  	

print(str(merkle(txHashes))[1:])

def rank_calc(block_header, stake, prestige):
    return int(block_header["nonce"]) / ((stake + 10*prestige)**20)
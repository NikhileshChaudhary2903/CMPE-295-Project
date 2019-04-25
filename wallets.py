def get_wallet():
    from OpenSSL import crypto
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode('utf8')
    public_key = crypto.dump_publickey(crypto.FILETYPE_PEM, key).decode('utf8')

    return {
        "public_key_string" : public_key,
        "private_key_string" : private_key
    }
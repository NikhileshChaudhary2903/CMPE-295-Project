from ecdsa import SigningKey, SECP256k1


def get_wallet():
    key = SigningKey.generate(curve=SECP256k1)
    private_key_string = key.to_pem().decode()
    public_key_string = key.get_verifying_key().to_pem().decode()

    return {
        "private_key_string": private_key_string,
        "public_key_string": public_key_string
    }

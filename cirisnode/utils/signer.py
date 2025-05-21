from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
import json
from typing import Dict # Import Dict

# Generate Ed25519 key pair
private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

def sign_data(data: Dict) -> bytes:
    """Sign the given data using the Ed25519 private key."""
    message = json.dumps(data, sort_keys=True).encode()
    signature = private_key.sign(message)
    return signature

def get_public_key_pem() -> str:
    """Return the Ed25519 public key in PEM format."""
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem.decode()

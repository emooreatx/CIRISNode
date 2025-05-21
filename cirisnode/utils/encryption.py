from cryptography.fernet import Fernet

# Generate a key for encryption/decryption
# This key should be securely stored and retrieved from a secure location (e.g., environment variable, secrets manager)
SECRET_KEY = Fernet.generate_key()
cipher = Fernet(SECRET_KEY)

def encrypt_data(data: str) -> str:
    """Encrypt the given data."""
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt the given data."""
    return cipher.decrypt(encrypted_data.encode()).decode()

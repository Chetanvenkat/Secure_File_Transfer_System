from cryptography.fernet import Fernet
from config import Config

# Master key (base64-encoded 32-byte key)
MASTER_KEY_STR = Config.FILE_MASTER_KEY
MASTER_KEY = MASTER_KEY_STR.encode("utf-8")

fernet_master = Fernet(MASTER_KEY)


def encrypt_file_bytes(data: bytes):
    """
    Encrypt raw file bytes using a random per-file Fernet key.
    Returns (ciphertext, encrypted_file_key).
    """
    # Generate random key for this file
    file_key = Fernet.generate_key()
    f = Fernet(file_key)

    # Encrypt file content
    ciphertext = f.encrypt(data)

    # Encrypt file key with master key
    encrypted_key = fernet_master.encrypt(file_key)
    return ciphertext, encrypted_key


def decrypt_file_bytes(ciphertext: bytes, encrypted_key: bytes) -> bytes:
    """
    Decrypt ciphertext using the encrypted per-file key.
    """
    file_key = fernet_master.decrypt(encrypted_key)
    f = Fernet(file_key)
    plaintext = f.decrypt(ciphertext)
    return plaintext

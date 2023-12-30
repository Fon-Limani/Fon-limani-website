import hashlib

from base64 import urlsafe_b64encode



class PasswordEncryptor:
    def __init__(self, secret_key):
        hashed_key = hashlib.sha256(secret_key.encode("utf-8")).digest()
        self.key = hashed_key[:32]

    def hash_password(self, password):
        hashed_password = hashlib.sha256(password.encode("utf-8")).digest()
        return urlsafe_b64encode(hashed_password).decode("utf-8")

    def verify_password(self, password, hashed_password) -> bool:
        return self.hash_password(password) == hashed_password
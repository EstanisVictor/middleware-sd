from cryptography.fernet import Fernet

class Crypto:
    def __init__(self, data):
        self.data = data
        #fazer a chave na parte dos controllers
        self.key = self.generate_key()

    def generate_key(self):
        return Fernet.generate_key()

    def encrypt_data(self):
        return Fernet(self.key).encrypt(self.data.encode())

    def descrypt_data(self):
        return Fernet(self.key).decrypt(self.data).decode()
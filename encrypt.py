from cryptography.fernet import Fernet

class Encrypt:
    def __init__(self, key=None):
        """
        Initialize the Encrypt class with a provided key.
        If no key is provided, a new key is generated.
        """
        # Generate a new key if one is not provided.
        if key is None:
            key = Fernet.generate_key()
        elif isinstance(key, str):
            # Ensure the key is bytes.
            key = key.encode()
            
        self.key = key
        self.fernet = Fernet(self.key)

    def encrypt_text(self, plain_text):
        """
        Encrypt a plaintext string.
        """
        # Encrypt the text after encoding it to bytes.
        encrypted_bytes = self.fernet.encrypt(plain_text.encode())
        # Return the encrypted text as a string.
        return encrypted_bytes.decode()

    def decrypt_text(self, cipher_text):
        """
        Decrypt an encrypted text string.
        """
        # Decrypt the text after encoding it to bytes.
        decrypted_bytes = self.fernet.decrypt(cipher_text.encode())
        # Return the original plain text.
        return decrypted_bytes.decode()


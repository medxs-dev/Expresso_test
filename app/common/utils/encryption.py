from cryptography.fernet import Fernet

# Ideally, move this key to a secure environment variable!
FERNET_KEY = b'7e3hxcm8o0VkY4xGqHNE7E3v6Fq_GAWLX5iBO_eX4U0='
f = Fernet(FERNET_KEY)


def encrypt_text(text: str) -> str:
    return f.encrypt(text.encode()).decode()


def decrypt_text(token: str) -> str:
    return f.decrypt(token.encode()).decode()

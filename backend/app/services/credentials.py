from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class CredentialVault:
    def _fernet(self) -> Fernet:
        key = get_settings().credentials_encryption_key
        if not key:
            raise RuntimeError("CREDENTIALS_ENCRYPTION_KEY is not configured")
        return Fernet(key.encode())

    def encrypt(self, value: str) -> str:
        return self._fernet().encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        try:
            return self._fernet().decrypt(value.encode()).decode()
        except InvalidToken as error:
            raise RuntimeError("Stored credential cannot be decrypted") from error

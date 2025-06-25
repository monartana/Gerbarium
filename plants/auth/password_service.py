from passlib.context import CryptContext


class PasswordService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_hash_password(self, plain_password):
        return self.pwd_context.hash(plain_password)

    def verify_password(self, plain_password, hash_password):
        return self.pwd_context.verify(plain_password, hash_password)


def get_password_service():
    return PasswordService()

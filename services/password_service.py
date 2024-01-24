import bcrypt
import random
import string


class PasswordService:
    def __init__(self) -> None:
        self.password_generator = PasswordGenerator(
            [
                PasswordPartGenerator(string.ascii_lowercase),
                PasswordPartGenerator(string.ascii_uppercase),
                PasswordPartGenerator(string.digits),
            ]
        )

    def create_hash(self, password: str) -> bytes:
        return self._gen_hash(password)

    def check(self, password, password_hash):
        return self._check(password, password_hash)

    def generate_password(self, length) -> str:
        return self.password_generator.generate_password(length)

    def _gen_hash(self, password: str) -> bytes:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(14))

    def _check(self, password: str, password_hash: bytes) -> bool:
        return bcrypt.checkpw(password.encode(), password_hash)


class PasswordPartGenerator:
    def __init__(self, characters):
        self.characters = characters

    def generate(self, length):
        random_characters = random.choices(self.characters, k=length)
        return random_characters


class PasswordGenerator:
    def __init__(self, generators: list):
        self.generators = generators

    def generate_password(self, length):
        sliced_generated_parts = []
        generated_parts = len(self.generators)
        for generator in self.generators[:-1]:
            sliced_length = random.randint(1, length - generated_parts + 1)
            generated_parts -= 1
            length -= sliced_length
            sliced_generated_parts.append(generator.generate(sliced_length))
        sliced_generated_parts.append(self.generators[-1].generate(length))

        password_characters = [
            item for sublist in sliced_generated_parts for item in sublist
        ]
        random.shuffle(password_characters)
        generated_password = "".join(password_characters)
        return generated_password

import jwt
import time
from jwt.exceptions import (
    InvalidTokenError,
    DecodeError,
    InvalidSignatureError,
    ExpiredSignatureError,
    InvalidIssuedAtError,
    MissingRequiredClaimError,
)


class TokensService:
    def __init__(self, env):
        self.jwt_secret = env.get_var("JWT_SECRET")
        self.access_token_ttl = env.get_var("ACCESS_TOKEN_TTL_MINUTES")
        self.refresh_token_ttl = env.get_var("REFRESH_TOKEN_TTL_DAYS")

    def encode(self, token_type, data):
        iat = time.time()
        if token_type == "access":
            exp = iat + 60 * self.access_token_ttl
        elif token_type == "refresh":
            exp = iat + 3600 * 24 * self.refresh_token_ttl
        token_data = {"iat": iat, "exp": exp, "purpose": token_type}
        payload = {**data, **token_data}
        token: str = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        return token

    def decode(self, token):
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
                options={
                    "require_exp": True,
                    "require_iat": True,
                    "verify_exp": True,
                    "verify_iat": True,
                },
            )
        except (
            InvalidTokenError,
            DecodeError,
            InvalidSignatureError,
            ExpiredSignatureError,
            InvalidIssuedAtError,
            MissingRequiredClaimError,
        ):
            payload = None
        return payload

from typing import Optional

import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import SecurityScopes, HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_processed_environment_variables


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """Returns HTTP 403"""
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthenticatedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication"
        )


class VerifyToken:
    """Does all the token verification using PyJWT"""
    def __init__(self):
        self.processed_environment_variables = get_processed_environment_variables()
        # This gets the JWKS from a given URL and does processing, so you can
        # use any of the keys available
        jwks_url = f'https://{self.processed_environment_variables.AUTH0_DOMAIN}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    async def verify(self,
                     security_scopes: SecurityScopes,
                     token: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer())
                     ):
        if token is None:
            raise UnauthenticatedException

        # This gets the 'kid' from the passed token
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(
                token.credentials
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            raise UnauthorizedException(str(error))
        except jwt.exceptions.DecodeError as error:
            raise UnauthorizedException(str(error))

        try:
            payload = jwt.decode(
                token.credentials,
                signing_key,
                algorithms=self.processed_environment_variables.AUTH0_ALGORITHMS,
                audience=self.processed_environment_variables.AUTH0_API_AUDIENCE,
                issuer=self.processed_environment_variables.AUTH0_ISSUER,
            )
        except Exception as error:
            raise UnauthorizedException(str(error))

        return payload

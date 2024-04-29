import jwt
from typing import Optional

from django.utils import timezone

from .config import (
    get_signing_key,
    get_signing_algorithm,
    get_access_token_lifetime,
    get_refresh_token_lifetime,
)
from .types import TokenType


def generate_access_token(payload: Optional[dict] = None) -> str:
    """
    Generates an access token.

    Parameters:
        payload (dict, optional): Additional payload data to include in the token.

    Returns:
        str: The generated access token.
    """
    access_token_payload = {
        "type": TokenType.ACCESS.value,
        "exp": timezone.now() + get_access_token_lifetime(),
        "iat": timezone.now(),
    } | (payload or {})

    access_token = jwt.encode(
        access_token_payload, get_signing_key(), algorithm=get_signing_algorithm()
    )

    return access_token


def generate_refresh_token(access_token: str, payload: Optional[dict] = None) -> str:
    """
    Generates a refresh token.

    Parameters:
        access_token (str): The generated access token.
        payload (dict, optional): Additional payload data to include in the refresh token.

    Returns:
        str: The generated refresh token.
    """
    payload = (payload or {}) | {"access_token": access_token}

    refresh_token_payload = {
        "type": TokenType.REFRESH.value,
        "exp": timezone.now() + get_refresh_token_lifetime(),
        "iat": timezone.now(),
    } | payload

    refresh_token = jwt.encode(
        refresh_token_payload, get_signing_key(), algorithm=get_signing_algorithm()
    )

    return refresh_token


def generate_token_pair(payload: Optional[dict] = None) -> tuple[str, str]:
    """
    Generates a pair of access and refresh tokens.

    Parameters:
        payload (dict, optional): Additional payload data to include in the tokens.

    Returns:
        tuple[str, str]: A tuple containing the generated access token and refresh token.
    """
    access_token = generate_access_token(payload)
    refresh_token = generate_refresh_token(access_token, payload)
    return access_token, refresh_token


def decode_token(token: str, options: Optional[dict] = None) -> dict:
    """
    Decodes a JWT token.

    Parameters:
        token (str): The token to be decoded.
        options (dict, optional): Additional decoding options. Defaults to None.

    Returns:
        dict: The decoded payload of the token.

    Raises:
        jwt.exceptions.DecodeError: If the token cannot be decoded.
        jwt.exceptions.ExpiredSignatureError: If the token has expired.
        jwt.exceptions.InvalidTokenError: If the token is invalid.
    """
    return jwt.decode(
        token,
        get_signing_key(),
        algorithms=[get_signing_algorithm()],
        options=options,
    )


def decode_token_no_exp(token: str) -> dict:
    """
    Decodes a JWT token without verifying the expiration time.

    Parameters:
        token (str): The token to be decoded.

    Returns:
        dict: The decoded payload of the token.

    Raises:
        jwt.exceptions.DecodeError: If the token cannot be decoded.
    """
    return decode_token(token, {"verify_exp": False})


def get_token_type(token: str) -> TokenType:
    """
    Gets the type of a JWT token.

    Parameters:
        token (str): The token to get the type of.

    Returns:
        TokenType: The type of the token.
    """
    try:
        payload = decode_token_no_exp(token)
        return TokenType(payload.get("type"))
    except jwt.exceptions.DecodeError:
        return TokenType.UNDEFINED


def get_request_token(request) -> str | None:
    """
    Gets the token from the request.
    """
    if "HTTP_AUTHORIZATION" in request.META:
        return request.META["HTTP_AUTHORIZATION"].replace("Bearer ", "")
    return request.COOKIES.get("access_token", None)


def get_request_refresh_token(request) -> str:
    """
    Gets the refresh token from the request.
    """
    if "HTTP_AUTHORIZATION" in request.META:
        return request.META["HTTP_AUTHORIZATION"].replace("Bearer ", "")
    return request.COOKIES.get("refresh_token", None)

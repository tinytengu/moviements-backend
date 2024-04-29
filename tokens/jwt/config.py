import datetime
from typing import Any

from django.conf import settings


def get_jwt_config(key: str, default: Any = None) -> Any:
    """
    get_jwt_config function retrieves a specific configuration value from the JWT_CONFIG dictionary in Django settings.

    Parameters:
        key (str): The key of the configuration value to retrieve.
        default (Any, optional): A default value to return if the specified key is not found in the JWT_CONFIG dictionary. Defaults to None.

    Returns:
        Any: The value associated with the specified key in the JWT_CONFIG dictionary, or the default value if the key is not found.
    """
    return settings.JWT_CONFIG.get(key, default)


def get_signing_key() -> str:
    """
    get_signing_key function retrieves the value of the "SIGNING_KEY" configuration from the JWT_CONFIG dictionary in Django settings.
    If the key is not found, it returns the default value, which is the Django SECRET_KEY.

    Returns:
        str: JWT signing key.
    """
    return get_jwt_config("SIGNING_KEY", settings.SECRET_KEY)


def get_signing_algorithm() -> str:
    """
    get_signing_algorithm function retrieves the value of the "SIGNING_ALGORITHM" configuration from the JWT_CONFIG dictionary in Django settings.

    Returns:
        str: JWT signing algorithm.
    """
    return get_jwt_config("SIGNING_ALGORITHM", "HS256")


def get_access_token_lifetime() -> datetime.timedelta:
    """
    get_access_token_lifetime function retrieves the value of the "ACCESS_TOKEN_LIFETIME" configuration from the JWT_CONFIG dictionary in Django settings.
    If the key is not found, it returns the default value, which is 5 minutes.

    Returns:
        datetime.timedelta: The lifetime of the access token in days and minutes.
    """
    return get_jwt_config(
        "ACCESS_TOKEN_LIFETIME", datetime.timedelta(days=0, minutes=5)
    )


def get_refresh_token_lifetime() -> datetime.timedelta:
    """
    get_refresh_token_lifetime function retrieves the value of the "REFRESH_TOKEN_LIFETIME" configuration from the JWT_CONFIG dictionary in Django settings.
    If the key is not found, it returns the default value, which is 30 days.

    Returns:
        datetime.timedelta: The lifetime of the refresh token in days and minutes.
    """
    return get_jwt_config("REFRESH_TOKEN_LIFETIME", datetime.timedelta(days=30))

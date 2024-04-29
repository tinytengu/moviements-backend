from django.test import TestCase

from .jwt import (
    generate_token_pair,
    generate_access_token,
    generate_refresh_token,
    decode_token,
    get_token_type,
)
from .jwt.types import TokenType


class TokensTestCase(TestCase):
    def test_generate_access_token(self):
        token = generate_access_token()
        decode_token(token)

        self.assertIsInstance(token, str)
        self.assertEqual(get_token_type(token), TokenType.ACCESS)

    def test_generate_refresh_token(self):
        access_token = generate_access_token()
        refresh_token = generate_refresh_token(access_token)

        self.assertIsInstance(refresh_token, str)
        self.assertEqual(get_token_type(refresh_token), TokenType.REFRESH)
        self.assertEqual(decode_token(refresh_token).get("access_token"), access_token)

    def test_generate_token_pair(self):
        token_pair = generate_token_pair()
        self.assertIsInstance(token_pair, tuple)
        self.assertIsInstance(token_pair[0], str)
        self.assertIsInstance(token_pair[1], str)

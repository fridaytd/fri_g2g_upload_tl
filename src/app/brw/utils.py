import base64
import json

from .models import JWTPayload


def decode_jwt(jwt_token: str) -> JWTPayload:
    """
    Decode a JWT token and return its payload without verification.

    Args:
        jwt_token (str): The JWT token to decode

    Returns:
        dict: The decoded payload as a dictionary

    Note: This function does NOT verify the token's signature. For production use,
    consider using a library like PyJWT that properly verifies tokens.
    """
    # Split the token into its three parts
    try:
        _, payload_b64, _ = jwt_token.split(".")

        # Decode the payload
        # JWT base64 is URL-safe, so we may need to add padding
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        return JWTPayload.model_validate(payload)
    except Exception as e:
        raise ValueError(f"Invalid JWT token format: {str(e)}")

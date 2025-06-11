from typing import Final

ACCESS_TOKEN_DELIVERED_VIA_COOKIE: Final[str] = (
    "Delivered auth session token via cookie."
)
ACCESS_TOKEN_INVALID_OR_EXPIRED: Final[str] = "Invalid or expired JWT."
ACCESS_TOKEN_MARKED_FOR_REMOVAL: Final[str] = (
    "Marked access token for removal in response."
)
ACCESS_TOKEN_NOT_FOUND_IN_COOKIE: Final[str] = "No access token found in cookie."
ACCESS_TOKEN_PAYLOAD_OF_INTEREST: Final[str] = "auth_session_id"
ACCESS_TOKEN_PAYLOAD_MISSING: Final[str] = "JWT payload missing."

COOKIE_ACCESS_TOKEN_NAME: Final[str] = "access_token"

REQUEST_STATE_COOKIE_PARAMS_KEY: Final[str] = "cookie_params"
REQUEST_STATE_DELETE_ACCESS_TOKEN_KEY: Final[str] = "delete_access_token"
REQUEST_STATE_NEW_ACCESS_TOKEN_KEY: Final[str] = "new_access_token"

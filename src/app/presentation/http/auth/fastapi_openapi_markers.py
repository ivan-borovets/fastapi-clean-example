from fastapi.security import APIKeyCookie

from app.presentation.http.auth.constants import (
    COOKIE_ACCESS_TOKEN_NAME,
)

# Token extraction marker for FastAPI OpenAPI.
# The actual token processing is handled behind the Identity Provider.
cookie_scheme = APIKeyCookie(name=COOKIE_ACCESS_TOKEN_NAME)

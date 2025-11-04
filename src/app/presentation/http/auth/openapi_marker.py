from fastapi.security import APIKeyCookie

from app.presentation.http.auth.constants import (
    COOKIE_ACCESS_TOKEN_NAME,
)

# Cookie extraction marker for Swagger UI (OpenAPI).
# The actual cookie processing is handled behind the Identity Provider.
cookie_scheme = APIKeyCookie(name=COOKIE_ACCESS_TOKEN_NAME)

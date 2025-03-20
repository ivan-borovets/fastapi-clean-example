from fastapi.security import APIKeyCookie

# Token extraction marker for FastAPI Swagger UI.
# The actual token processing will be handled behind the Identity Provider.
cookie_scheme = APIKeyCookie(name="access_token")

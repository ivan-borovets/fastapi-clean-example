from fastapi.security import APIKeyCookie

# Token extraction marker for FastAPI Swagger UI.
# The actual token processing will be handled inside the Identity Provider.
cookie_scheme: APIKeyCookie = APIKeyCookie(name="access_token")

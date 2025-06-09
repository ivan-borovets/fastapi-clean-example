from typing import Final

AUTH_ACCOUNT_INACTIVE: Final[str] = "Your account is inactive. Please contact support."
AUTH_ALREADY_AUTHENTICATED: Final[str] = (
    "You are already authenticated. Consider logging out."
)
AUTH_INVALID_PASSWORD: Final[str] = "Invalid password."
AUTH_IS_UNAVAILABLE: Final[str] = (
    "Authentication is currently unavailable. Please try again later."
)
AUTH_NOT_AUTHENTICATED: Final[str] = "Not authenticated."
AUTH_SESSION_NOT_FOUND: Final[str] = "Session not found."
AUTH_SESSION_EXPIRED: Final[str] = "Session expired."
AUTH_SESSION_EXTENSION_FAILED: Final[str] = "Auth session extension failed."
AUTH_SESSION_EXTRACTION_FAILED: Final[str] = "Auth session extraction failed."

DB_CONSTRAINT_VIOLATION: Final[str] = "Database constraint violation."
DB_COMMIT_DONE: Final[str] = "Commit was done."
DB_COMMIT_FAILED: Final[str] = "Commit failed."
DB_FLUSH_DONE: Final[str] = "Flush was done."
DB_FLUSH_FAILED: Final[str] = "Flush failed."
DB_QUERY_FAILED: Final[str] = "Database query failed."

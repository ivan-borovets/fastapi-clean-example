from datetime import timedelta
from typing import Literal, NewType

# security.auth
JwtSecret = NewType("JwtSecret", str)
JwtAlgorithm = Literal["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
AuthSessionTtlMin = NewType("AuthSessionTtlMin", timedelta)
AuthSessionRefreshThreshold = NewType("AuthSessionRefreshThreshold", float)

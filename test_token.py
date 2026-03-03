import jwt
from app.core.config import settings

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjIsImlhdCI6MTczMzA1Njk5NX0.0CZ2OPZ45jRUEefIcxLtso7yRxKotrzMsRc3IsEHC5o"

print(f"Secret: {settings.SECRET_KEY}")
print(f"Algorithm: {settings.ALGORITHM}")

try:
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(f"Decoded: {decoded}")
except Exception as e:
    print(f"Error: {e}")

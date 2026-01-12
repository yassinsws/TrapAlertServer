from auth import create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
import time

try:
    token = create_access_token({"sub": 1})
    print(f"Token: {token}")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(f"Payload: {payload}")
    print("✓ Success")
except JWTError as e:
    print(f"❌ JWTError: {e}")
except Exception as e:
    print(f"❌ Other Error: {e}")

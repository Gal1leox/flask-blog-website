import secrets

token = secrets.token_urlsafe(32)
print(f"The secret token:", token)

from datetime import datetime, timedelta, timezone

import jwt

import os
from pathlib import Path

from dotenv import load_dotenv
from pwdlib import PasswordHash

# Configure Argon2 password hashing
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Convert a plaintext password into a secure hash."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Check whether a password matches its stored hash."""
    return password_hash.verify(
        plain_password,
        hashed_password,
    )
# Load environment variables from the project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

# Never start authentication without a signing secret
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured")

# Generate a signed JWT access token for an authenticated user
def create_access_token(subject: str) -> str:
    """Create a JWT that expires after the configured duration."""

    # Calculate when the token expires
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Store the user's identity and expiration in the token
    payload = {
        "sub": subject,
        "exp": expires_at,
    }

    # Sign the token using our private secret key
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """Validate incoming user registration data."""

    email: str = Field(
        min_length=3,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    """Return public user information without passwords."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_active: bool

class UserLogin(BaseModel):
    """Validate incoming user login credentials."""

    email: str = Field(
        min_length=3,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )

    password: str = Field(
        min_length=1,
    )

class TokenResponse(BaseModel):
    """Return a JWT access token after successful login."""

    access_token: str
    token_type: str = "bearer"
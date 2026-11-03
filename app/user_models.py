
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


# Store registered users and their authentication details
class User(Base):
    __tablename__ = "users"

    # Unique identifier for each user
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    # Email address used to log in
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    # Store a password hash, never the original password
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    # Allow accounts to be activated or deactivated
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

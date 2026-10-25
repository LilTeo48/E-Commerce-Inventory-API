
from decimal import Decimal

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    stock_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

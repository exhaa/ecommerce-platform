from decimal import Decimal

from pydantic import BaseModel, Field


class ProductSchema(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=200
    )

    description: str | None = Field(
        default=None,
        max_length=1000
    )

    price: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2
    )

    stock: int = Field(
        ge=0
    )

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product
from app.schemas import (
    InventoryAdjustment,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

from decimal import Decimal

from app.order_models import Order, OrderItem
from app.schemas import OrderCreate, OrderResponse


# Initialize the FastAPI application
app = FastAPI(
    title="E-Commerce Inventory & Order Management API",
    description="A REST API for managing e-commerce inventory and orders.",
    version="1.0.0",
)


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to the E-Commerce Inventory API!",
        "status": "running",
    }


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ecommerce-api",
    }


# Create a new product
@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    new_product = Product(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# Retrieve all products
@app.get("/products", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.scalars(select(Product)).all()
    return products


# Retrieve a single product by ID
@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


# Update an existing product
@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    for field, value in product_data.model_dump().items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


# Delete an existing product
@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    db.delete(product)
    db.commit()


# Adjust inventory for an existing product
@app.patch(
    "/products/{product_id}/inventory",
    response_model=ProductResponse,
)
def adjust_inventory(
    product_id: int,
    adjustment: InventoryAdjustment,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    new_quantity = product.stock_quantity + adjustment.quantity_change

    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock",
        )

    product.stock_quantity = new_quantity

    db.commit()
    db.refresh(product)

    return product

# Create a new customer order
@app.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)


def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
):
    # Collect unique product IDs in a consistent order
    product_ids = sorted({
        item.product_id for item in order_data.items
    })

    # Retrieve and lock the requested products
    products = db.scalars(
        select(Product)
        .where(Product.id.in_(product_ids))
        .order_by(Product.id)
        .with_for_update()
    ).all()

    # Build a dictionary for quick product lookup
    products_by_id = {
        product.id: product for product in products
    }

    # Verify that every requested product exists
    for item in order_data.items:
        if item.product_id not in products_by_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found",
            )

    # Combine quantities when the same product appears more than once
    requested_quantities = {}

    for item in order_data.items:
        requested_quantities[item.product_id] = (
            requested_quantities.get(item.product_id, 0)
            + item.quantity
        )

    # Verify sufficient inventory exists for every product
    for product_id, quantity in requested_quantities.items():
        product = products_by_id[product_id]

        if product.stock_quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product_id}",
            )

    # Calculate the order total using database prices
    total_amount = Decimal("0.00")

    for product_id, quantity in requested_quantities.items():
        product = products_by_id[product_id]
        total_amount += product.price * quantity


    # Create a new order
    new_order = Order(
        status="pending",
        total_amount=total_amount,
    )

    # Create order items using the current product prices
    for product_id, quantity in requested_quantities.items():
        product = products_by_id[product_id]

        order_item = OrderItem(
            product_id=product_id,
            quantity=quantity,
            unit_price=product.price,
        )

        new_order.items.append(order_item)

    # Stage the order and its items for database insertion
    db.add(new_order)



    # Deduct purchased quantities from inventory
    for product_id, quantity in requested_quantities.items():
        product = products_by_id[product_id]
        product.stock_quantity -= quantity

    # Save the order, order items, and inventory changes together
    db.commit()

    # Reload the saved order
    db.refresh(new_order)

    return new_order


# Retrieve all customer orders
@app.get("/orders", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    orders = db.scalars(
        select(Order).order_by(Order.id)
    ).all()

    return orders


# Retrieve a single customer order by ID
@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = db.get(Order, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order




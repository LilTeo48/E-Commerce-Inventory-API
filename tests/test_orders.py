
def test_create_order_success(client):
    # Create a product with 10 units in stock
    product_response = client.post(
        "/products",
        json={
            "name": "Gaming Keyboard",
            "description": "Mechanical gaming keyboard",
            "price": "49.99",
            "stock_quantity": 10,
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    # Purchase 3 units of the product
    order_response = client.post(
        "/orders",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 3,
                }
            ]
        },
    )

    assert order_response.status_code == 201

    order = order_response.json()

    assert order["status"] == "pending"
    assert float(order["total_amount"]) == 149.97
    assert len(order["items"]) == 1
    assert order["items"][0]["product_id"] == product_id
    assert order["items"][0]["quantity"] == 3

    # Verify that inventory was reduced from 10 to 7
    inventory_response = client.get(f"/products/{product_id}")

    assert inventory_response.status_code == 200
    assert inventory_response.json()["stock_quantity"] == 7


def test_create_order_insufficient_stock(client):
    # Create a product with only 5 units available
    product_response = client.post(
        "/products",
        json={
            "name": "Wireless Mouse",
            "description": "Bluetooth wireless mouse",
            "price": "24.99",
            "stock_quantity": 5,
        },
    )

    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    # Attempt to purchase 10 units
    order_response = client.post(
        "/orders",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 10,
                }
            ]
        },
    )

    # The API should reject the order
    assert order_response.status_code == 400
    assert order_response.json()["detail"] == (
        f"Insufficient stock for product {product_id}"
    )

    # Verify inventory remains unchanged
    inventory_response = client.get(f"/products/{product_id}")

    assert inventory_response.status_code == 200
    assert inventory_response.json()["stock_quantity"] == 5


def test_create_order_product_not_found(client):
    # Attempt to order a product that does not exist
    response = client.post(
        "/orders",
        json={
            "items": [
                {
                    "product_id": 999999,
                    "quantity": 2,
                }
            ]
        },
    )

    # The API should return 404 Not Found
    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Product 999999 not found"
    )


def test_create_order_duplicate_products(client):
    # Create a product with 10 units available
    product_response = client.post(
        "/products",
        json={
            "name": "Gaming Mouse",
            "description": "Wireless gaming mouse",
            "price": "25.00",
            "stock_quantity": 10,
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    # Request the same product twice
    response = client.post(
        "/orders",
        json={
            "items": [
                {"product_id": product_id, "quantity": 3},
                {"product_id": product_id, "quantity": 4},
            ]
        },
    )

    assert response.status_code == 201
    assert response.json()["total_amount"] == "175.00"

    # Verify inventory was reduced by 7, not 3 or 4
    inventory_response = client.get(f"/products/{product_id}")
    assert inventory_response.status_code == 200
    assert inventory_response.json()["stock_quantity"] == 3

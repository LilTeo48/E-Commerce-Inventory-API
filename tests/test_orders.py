
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


def test_get_orders_empty(client):
    # Retrieve orders when the database has no orders
    response = client.get("/orders")

    # Verify the API returns an empty list
    assert response.status_code == 200
    assert response.json() == []


def test_get_orders_with_existing_order(client):
    # Create a product
    product_response = client.post(
        "/products",
        json={
            "name": "Gaming Headset",
            "description": "Wireless gaming headset",
            "price": "79.99",
            "stock_quantity": 10,
        },
    )

    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    # Create an order for two headsets
    order_response = client.post(
        "/orders",
        json={
            "items": [
                {"product_id": product_id, "quantity": 2}
            ]
        },
    )

    assert order_response.status_code == 201
    order_id = order_response.json()["id"]

    # Retrieve all orders
    response = client.get("/orders")

    assert response.status_code == 200

    orders = response.json()

    assert len(orders) == 1
    assert orders[0]["id"] == order_id
    assert orders[0]["status"] == "pending"
    assert float(orders[0]["total_amount"]) == 159.98
    assert len(orders[0]["items"]) == 1
    assert orders[0]["items"][0]["quantity"] == 2


def test_get_order_not_found(client):
    # Attempt to retrieve an order that does not exist
    response = client.get("/orders/999999")

    # Verify the API returns HTTP 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_get_order_by_id(client):
    # Create a product
    product_response = client.post(
        "/products",
        json={
            "name": "Gaming Monitor",
            "description": "27-inch gaming monitor",
            "price": "199.99",
            "stock_quantity": 5,
        },
    )

    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    # Create an order for one monitor
    order_response = client.post(
        "/orders",
        json={
            "items": [
                {"product_id": product_id, "quantity": 1}
            ]
        },
    )

    assert order_response.status_code == 201
    order_id = order_response.json()["id"]

    # Retrieve the order using its ID
    response = client.get(f"/orders/{order_id}")

    assert response.status_code == 200

    order = response.json()

    # Verify the retrieved order details
    assert order["id"] == order_id
    assert order["status"] == "pending"
    assert order["total_amount"] == "199.99"
    assert len(order["items"]) == 1
    assert order["items"][0]["product_id"] == product_id
    assert order["items"][0]["quantity"] == 1

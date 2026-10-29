
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


def test_cancel_order_restores_inventory(client):
    # Create a product with 10 units in stock
    product_response = client.post(
        "/products",
        json={
            "name": "Gaming Keyboard",
            "description": "Mechanical keyboard",
            "price": "79.99",
            "stock_quantity": 10,
        },
    )

    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    # Purchase 3 keyboards
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
    order_id = order_response.json()["id"]

    # Verify inventory decreased from 10 to 7
    stock_response = client.get(f"/products/{product_id}")
    assert stock_response.json()["stock_quantity"] == 7

    # Cancel the order
    cancel_response = client.patch(
        f"/orders/{order_id}/cancel"
    )

    # Verify the order was cancelled
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

    # Verify inventory was restored from 7 to 10
    restored_response = client.get(f"/products/{product_id}")
    assert restored_response.json()["stock_quantity"] == 10

def test_cancel_order_twice_returns_400(client):
    # Create a product with 10 units
    product_response = client.post(
        "/products",
        json={
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse",
            "price": "29.99",
            "stock_quantity": 10,
        },
    )

    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    # Purchase 4 units
    order_response = client.post(
        "/orders",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 4,
                }
            ]
        },
    )

    assert order_response.status_code == 201
    order_id = order_response.json()["id"]

    # Cancel successfully the first time
    first_cancel = client.patch(
        f"/orders/{order_id}/cancel"
    )

    assert first_cancel.status_code == 200

    # Attempt to cancel the same order again
    second_cancel = client.patch(
        f"/orders/{order_id}/cancel"
    )

    assert second_cancel.status_code == 400
    assert second_cancel.json()["detail"] == (
        "Only pending orders can be cancelled"
    )

    # Inventory should remain at 10, not increase to 14
    product_check = client.get(f"/products/{product_id}")

    assert product_check.status_code == 200
    assert product_check.json()["stock_quantity"] == 10

def test_cancel_nonexistent_order_returns_404(client):
    # Attempt to cancel an order that does not exist
    response = client.patch(
        "/orders/999999/cancel"
    )

    # Verify the API returns 404 Not Found
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_cancel_order_restores_multiple_products(client):
    # Create two products
    keyboard_response = client.post(
        "/products",
        json={
            "name": "Mechanical Keyboard",
            "description": "RGB mechanical keyboard",
            "price": "89.99",
            "stock_quantity": 10,
        },
    )

    mouse_response = client.post(
        "/products",
        json={
            "name": "Gaming Mouse",
            "description": "Wireless gaming mouse",
            "price": "39.99",
            "stock_quantity": 20,
        },
    )

    assert keyboard_response.status_code == 201
    assert mouse_response.status_code == 201

    keyboard_id = keyboard_response.json()["id"]
    mouse_id = mouse_response.json()["id"]

    # Purchase 3 keyboards and 5 mice
    order_response = client.post(
        "/orders",
        json={
            "items": [
                {"product_id": keyboard_id, "quantity": 3},
                {"product_id": mouse_id, "quantity": 5},
            ]
        },
    )

    assert order_response.status_code == 201
    order_id = order_response.json()["id"]

    # Confirm inventory was deducted
    keyboard_stock = client.get(f"/products/{keyboard_id}")
    mouse_stock = client.get(f"/products/{mouse_id}")

    assert keyboard_stock.json()["stock_quantity"] == 7
    assert mouse_stock.json()["stock_quantity"] == 15

    # Cancel the order
    cancel_response = client.patch(
        f"/orders/{order_id}/cancel"
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

    # Verify both products have their original inventory
    restored_keyboard = client.get(f"/products/{keyboard_id}")
    restored_mouse = client.get(f"/products/{mouse_id}")

    assert restored_keyboard.status_code == 200
    assert restored_mouse.status_code == 200

    assert restored_keyboard.json()["stock_quantity"] == 10
    assert restored_mouse.json()["stock_quantity"] == 20

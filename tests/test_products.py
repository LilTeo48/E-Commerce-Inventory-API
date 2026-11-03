
def test_create_product(client):
    # Arrange: prepare a new product
    product_data = {
        "name": "Mechanical Keyboard",
        "description": "RGB mechanical gaming keyboard",
        "price": "89.99",
        "stock_quantity": 15,
    }

    # Act: send a POST request to our API
    response = client.post("/products", json=product_data)

    # Assert: verify the API response
    assert response.status_code == 201

    data = response.json()

    assert isinstance(data["id"], int)
    assert data["name"] == "Mechanical Keyboard"
    assert data["description"] == "RGB mechanical gaming keyboard"
    assert data["price"] == "89.99"
    assert data["stock_quantity"] == 15



def test_get_products(client):
    # Create a product in our isolated test database
    product_data = {
        "name": "Gaming Headset",
        "description": "Wireless gaming headset",
        "price": "79.99",
        "stock_quantity": 10,
    }

    create_response = client.post(
        "/products",
        json=product_data,
    )

    assert create_response.status_code == 201

    # Retrieve all products
    response = client.get("/products")

    assert response.status_code == 200

    products = response.json()

    assert isinstance(products, list)
    assert any(
        product["name"] == "Gaming Headset"
        for product in products
    )


def test_get_product_by_id(client):
    # Create a product
    product_data = {
        "name": "USB-C Hub",
        "description": "Multi-port USB-C adapter",
        "price": "39.99",
        "stock_quantity": 20,
    }

    create_response = client.post(
        "/products",
        json=product_data,
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    # Retrieve that exact product
    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["name"] == "USB-C Hub"
    assert response.json()["price"] == "39.99"

def test_get_product_not_found(client):
    response = client.get("/products/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

def test_create_product_negative_price(client):
    product_data = {
        "name": "Gaming Mouse",
        "description": "Wireless gaming mouse",
        "price": "-49.99",
        "stock_quantity": 10,
    }

    response = client.post("/products", json=product_data)

    assert response.status_code == 422

def test_create_product_negative_stock(client):
    product_data = {
        "name": "Gaming Monitor",
        "description": "27-inch gaming monitor",
        "price": "249.99",
        "stock_quantity": -10,
    }

    response = client.post("/products", json=product_data)

    assert response.status_code == 422


def test_update_product(client):
    # Create a product first
    product_data = {
        "name": "Gaming Keyboard",
        "description": "Mechanical gaming keyboard",
        "price": "89.99",
        "stock_quantity": 10,
    }

    create_response = client.post("/products", json=product_data)
    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    # Update the product
    updated_data = {
        "name": "Gaming Keyboard Pro",
        "description": "Upgraded mechanical gaming keyboard",
        "price": "119.99",
        "stock_quantity": 25,
    }

    response = client.put(
        f"/products/{product_id}",
        json=updated_data,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == "Gaming Keyboard Pro"
    assert data["description"] == "Upgraded mechanical gaming keyboard"
    assert data["price"] == "119.99"
    assert data["stock_quantity"] == 25



def test_update_product_not_found(client):
    updated_data = {
        "name": "Gaming Keyboard Pro",
        "description": "Upgraded mechanical keyboard",
        "price": "119.99",
        "stock_quantity": 25,
    }

    response = client.put(
        "/products/999999",
        json=updated_data,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product_negative_price(client):
    product_data = {
        "name": "Gaming Mouse",
        "description": "Wireless gaming mouse",
        "price": "49.99",
        "stock_quantity": 10,
    }

    create_response = client.post("/products", json=product_data)
    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    updated_data = {
        "name": "Gaming Mouse Pro",
        "description": "Upgraded wireless gaming mouse",
        "price": "-59.99",
        "stock_quantity": 15,
    }

    response = client.put(
        f"/products/{product_id}",
        json=updated_data,
    )

    assert response.status_code == 422


def test_delete_product(client):
    # Create a product
    product_data = {
        "name": "Gaming Mouse",
        "description": "Wireless gaming mouse",
        "price": "49.99",
        "stock_quantity": 10,
    }

    create_response = client.post("/products", json=product_data)
    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    # Delete the product
    delete_response = client.delete(f"/products/{product_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    # Verify the product no longer exists
    get_response = client.get(f"/products/{product_id}")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Product not found"


def test_delete_product_not_found(client):
    response = client.delete("/products/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"



def test_add_inventory(client):
    # Create a product with 10 units in stock
    product_data = {
        "name": "Gaming Keyboard",
        "description": "Mechanical gaming keyboard",
        "price": "89.99",
        "stock_quantity": 10,
    }

    create_response = client.post("/products", json=product_data)
    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    # Add 5 units to inventory
    response = client.patch(
        f"/products/{product_id}/inventory",
        json={"quantity_change": 5},
    )

    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 15

    # Verify the updated quantity was saved
    get_response = client.get(f"/products/{product_id}")

    assert get_response.status_code == 200
    assert get_response.json()["stock_quantity"] == 15



def test_remove_inventory(client):
    # Create a product with 20 units
    product_data = {
        "name": "Gaming Mouse",
        "description": "Wireless gaming mouse",
        "price": "49.99",
        "stock_quantity": 20,
    }

    create_response = client.post("/products", json=product_data)
    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    # Remove 5 units
    response = client.patch(
        f"/products/{product_id}/inventory",
        json={"quantity_change": -5},
    )

    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 15

    # Verify the database saved the new quantity
    get_response = client.get(f"/products/{product_id}")

    assert get_response.status_code == 200
    assert get_response.json()["stock_quantity"] == 15


def test_remove_inventory_insufficient_stock(client):
    # Create a product with 10 units available
    product_data = {
        "name": "Gaming Keyboard",
        "description": "Mechanical gaming keyboard",
        "price": "79.99",
        "stock_quantity": 10,
    }

    create_response = client.post("/products", json=product_data)
    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    # Attempt to remove more units than available
    response = client.patch(
        f"/products/{product_id}/inventory",
        json={"quantity_change": -15},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient stock"

    # Inventory should remain unchanged
    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["stock_quantity"] == 10

def test_search_products_by_name(client):
    # Create products with different names
    product_names = [
        "Mechanical Keyboard",
        "Wireless Mouse",
        "Gaming Keyboard",
    ]

    for name in product_names:
        response = client.post(
            "/products",
            json={
                "name": name,
                "description": "Gaming accessory",
                "price": "49.99",
                "stock_quantity": 10,
            },
        )

        assert response.status_code == 201

    # Search using lowercase to verify case-insensitive matching
    response = client.get("/products?search=keyboard")

    assert response.status_code == 200

    products = response.json()
    returned_names = [product["name"] for product in products]

    # Both keyboards should match, but the mouse should not
    assert returned_names == [
        "Mechanical Keyboard",
        "Gaming Keyboard",
    ]

def test_filter_products_by_price_range(client):
    # Create products at three different price points
    products = [
        ("Budget Mouse", "19.99"),
        ("Gaming Keyboard", "79.99"),
        ("Gaming Monitor", "249.99"),
    ]

    for name, price in products:
        response = client.post(
            "/products",
            json={
                "name": name,
                "description": "Gaming accessory",
                "price": price,
                "stock_quantity": 10,
            },
        )

        assert response.status_code == 201

    # Request products priced between $50 and $100
    response = client.get(
        "/products?min_price=50&max_price=100"
    )

    assert response.status_code == 200

    returned_names = [
        product["name"] for product in response.json()
    ]

    # Only the keyboard falls within this price range
    assert returned_names == ["Gaming Keyboard"]

def test_filter_products_by_stock_availability(client):
    # Create products with different stock quantities
    products = [
        ("Gaming Keyboard", 10),
        ("Wireless Mouse", 0),
        ("Gaming Headset", 5),
    ]

    for name, stock in products:
        response = client.post(
            "/products",
            json={
                "name": name,
                "description": "Gaming accessory",
                "price": "49.99",
                "stock_quantity": stock,
            },
        )

        assert response.status_code == 201

    # Retrieve only products currently in stock
    response = client.get("/products?in_stock=true")

    assert response.status_code == 200

    returned_names = [
        product["name"] for product in response.json()
    ]

    assert returned_names == [
        "Gaming Keyboard",
        "Gaming Headset",
    ]

    # Retrieve only out-of-stock products
    response = client.get("/products?in_stock=false")

    assert response.status_code == 200

    returned_names = [
        product["name"] for product in response.json()
    ]

    assert returned_names == ["Wireless Mouse"]

def test_products_combined_filters(client):
    # Create products with different names, prices, and stock
    products = [
        ("Gaming Keyboard", "79.99", 10),
        ("Budget Keyboard", "29.99", 5),
        ("Premium Keyboard", "149.99", 0),
        ("Gaming Mouse", "59.99", 10),
    ]

    for name, price, stock in products:
        response = client.post(
            "/products",
            json={
                "name": name,
                "description": "Gaming accessory",
                "price": price,
                "stock_quantity": stock,
            },
        )

        assert response.status_code == 201

    # Search for available keyboards priced $50-$200
    response = client.get(
        "/products?search=keyboard"
        "&min_price=50"
        "&max_price=200"
        "&in_stock=true"
    )

    assert response.status_code == 200

    returned_names = [
        product["name"] for product in response.json()
    ]

    # Only the gaming keyboard meets every condition
    assert returned_names == ["Gaming Keyboard"]

def test_products_invalid_price_filters_return_422(client):
    # Negative minimum price should be rejected
    response = client.get("/products?min_price=-10")

    assert response.status_code == 422

    # Negative maximum price should be rejected
    response = client.get("/products?max_price=-50")

    assert response.status_code == 422

    # Non-numeric price should be rejected
    response = client.get("/products?min_price=abc")

    assert response.status_code == 422

def test_products_reversed_price_range_returns_422(client):
    # Request a price range where the minimum exceeds the maximum
    response = client.get(
        "/products?min_price=200&max_price=50"
    )

    # The API should reject the invalid range
    assert response.status_code == 422

    # Verify the error message explains the problem
    assert response.json()["detail"] == (
        "min_price cannot be greater than max_price"
    )
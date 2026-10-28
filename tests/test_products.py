
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
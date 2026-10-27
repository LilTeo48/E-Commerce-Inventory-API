
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

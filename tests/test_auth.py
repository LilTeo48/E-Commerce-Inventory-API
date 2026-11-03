
def test_register_user_success(client):
    # Register a new user
    response = client.post(
        "/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "SecurePassword123!",
        },
    )

    # Registration should succeed
    assert response.status_code == 201

    # Verify the returned user information
    data = response.json()

    assert isinstance(data["id"], int)
    assert data["email"] == "testuser@example.com"
    assert data["is_active"] is True

    # Never expose passwords or password hashes
    assert "password" not in data
    assert "hashed_password" not in data

def test_register_duplicate_email_returns_409(client):
    # Register the first user
    first_response = client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "SecurePassword123!",
        },
    )

    assert first_response.status_code == 201

    # Attempt to register another user with the same email
    second_response = client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "AnotherPassword456!",
        },
    )

    # The API should reject duplicate email addresses
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "Email already registered"
    )
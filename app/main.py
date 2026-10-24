
from fastapi import FastAPI

app = FastAPI(
    title="E-Commerce Inventory & Order Management API",
    description="A REST API for managing e-commerce inventory and orders.",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to the E-Commerce Inventory API!",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ecommerce-api"
    }

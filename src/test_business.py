import os
import shutil
import json
from fastapi.testclient import TestClient
from tortoise.contrib.test import finalizer, initializer
from src.main import app
from src.business.schemas import UserBusiness, UserProduct
from src.models import User

client = TestClient(app)

TEST_USER = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpassword",
}

TEST_BUSINESS = {
    "business_name": "Test Business",
    "logo": "test_logo.png",
    "website": "https://testbusiness.com",
    "business_description": "A test business",
    "company_number": "1234567890",
    "vat_number": "9876543210",
}

TEST_PRODUCT = {
    "name": "Test Product",
    "category": "TestCategory",
    "price": 100.0,
    "description": "A test product",
    "cost": 50.0,
}

# Set up and tear down Tortoise ORM
def setup_module(module):
    initializer(["src.models"])


def teardown_module(module):
    finalizer()


async def get_access_token(user):
    response = client.post(
        "/auth/register",
        data=json.dumps(user),
        headers={"Content-Type": "application/json"},
    )
    response = client.post(
        "/auth/login",
        data=json.dumps({"username": user["username"], "password": user["password"]}),
        headers={"Content-Type": "application/json"},
    )
    access_token = response.json()["access_token"]
    return access_token


async def create_test_business(access_token):
    response = client.post(
        "/business/add",
        data=json.dumps(TEST_BUSINESS),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
    )
    return response.json()["data"]["id"]


async def create_test_product(access_token, business_id):
    response = client.post(
        f"/business/product/add/{business_id}",
        data=json.dumps(TEST_PRODUCT),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
    )
    return response.json()["data"]["id"]


async def test_add_user_business():
    access_token = await get_access_token(TEST_USER)
    response = client.post(
        "/business/add",
        data=json.dumps(TEST_BUSINESS),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["business_name"] == TEST_BUSINESS["business_name"]


async def test_get_user_businesses():
    access_token = await get_access_token(TEST_USER)
    response = client.get(
        "/business/all",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0


async def test_get_specific_user_business():
    access_token = await get_access_token(TEST_USER)
    business_id = await create_test_business(access_token)
    response = client.get(
        f"/business/get/{business_id}",
    )
    assert response.status_code == 200
    assert response.json()["data"]["id"] == business_id


async def test_update_user_business():
    access_token = await get_access_token(TEST_USER)
    business_id = await create_test_business(access_token)
    update_data = {
        "business_name": "Updated Test Business",
        "logo": "updated_logo.png",
        "website": "https://updatedtestbusiness.com",
        "business_description": "An updated test business",
        "company_number": "9876543210",
        "vat_number": "1234567890",
    }
    response = client.put(
        f"/business/update/{business_id}",
        data=json.dumps(update_data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["business_name"] == update_data["business_name"]


async def test_delete_user_business():
    access_token = await get_access_token(TEST_USER)
    business_id = await create_test_business(access_token)
    response = client.delete(
        f"/business/delete/{business_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["response"] == "Successfully deleted User Business and associated products"


async def test_add_user_product():
    access_token = await get_access_token(TEST_USER)
    business_id = await create_test_business(access_token)
    response = client.post(
        f"/business/product/add/{business_id}",
        data=json.dumps(TEST_PRODUCT),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == TEST_PRODUCT["name"]


async def test_get_all_business_products():
    access_token = await get_access_token(TEST_USER)
    business_id = await create_test_business(access_token)
    response = client.get(
        f"/business/{business_id}/get/products",
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0


async def test_get_specific_user_product():
    access_token = await get_access_token(TEST_USER)
    business_id = await create_test_business(access_token)
    product_id = await create_test_product(access_token, business_id)
    response = client.get(
        f"/business/product/get/{product_id}",
    )
    assert response.status_code == 200
    assert response.json()["data"]["id"] == product_id


async def test_update_user_product():
    access_token = await get_access_token(TEST_USER)
    business_id = await create_test_business(access_token)
    product_id = await create_test_product(access_token, business_id)
    update_data = {
        "name": "Updated Test Product",
        "category": "UpdatedTestCategory",
        "price": 150.0,
        "description": "An updated test product",
        "cost": 75.0,
    }
    response = client.put(
        f"/business/product/update/{product_id}",
        data=json.dumps(update_data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == update_data["name"]


async def test_delete_user_product():
    access_token = await get_access_token(TEST_USER)
    business_id = await create_test_business(access_token)
    product_id = await create_test_product(access_token, business_id)
    response = client.delete(
        f"/business/product/delete/{product_id}",
    )
    assert response.status_code == 200
    assert response.json()["message"] == "product successfully deleted"


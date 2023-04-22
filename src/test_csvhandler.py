import io
import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from main import app  # Replace "main" with the name of your main FastAPI app file

client = TestClient(app)

def create_csv_upload_file(content: str) -> UploadFile:
    return UploadFile(file=io.StringIO(content), filename="products.csv", content_type="text/csv")

@pytest.mark.asyncio
async def test_successful_csv_upload():
    content = "name,category,price,description\nitem1,category1,10,description1\nitem2,category2,20,description2"
    response = client.post("/csv_products", files={"file": create_csv_upload_file(content)})
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "data": [
            {"name": "item1", "category": "category1", "price": "10", "description": "description1"},
            {"name": "item2", "category": "category2", "price": "20", "description": "description2"},
        ],
    }

@pytest.mark.asyncio
async def test_invalid_csv_upload():
    content = "name;category;price;description\nitem1;category1;10;description1\nitem2;category2;20;description2"
    response = client.post("/csv_products", files={"file": create_csv_upload_file(content)})
    assert response.status_code == 422  # Unprocessable Entity
    assert "CsvFileException" in response.json()["detail"]

@pytest.mark.asyncio
async def test_empty_csv_upload():
    content = ""
    response = client.post("/csv_products", files={"file": create_csv_upload_file(content)})
    assert response.status_code == 422  # Unprocessable Entity
    assert "CsvFileException" in response.json()["detail"]

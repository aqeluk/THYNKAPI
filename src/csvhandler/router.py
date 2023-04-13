import csv
import io
from fastapi import UploadFile, File, APIRouter
from src.csvhandler.exceptions import CsvFileException
from src.exceptions import ServerErrorException


router = APIRouter(
    prefix="/csv_products",
    tags=["CSV"]
    )


@router.post('/')
async def csv_wholesale_products(file: UploadFile = File(...)):
    try:
        csv_file = file.file
        csv_reader = csv.DictReader(io.StringIO(csv_file.read().decode('utf-8')))
        products = []
        try:
            for row in csv_reader:
                try:
                    products.append(row)
                except Exception as e:
                    raise ServerErrorException(str(e))
        except Exception as e:
            raise CsvFileException(str(e))
        return {"status": "ok", "data": products}
    except Exception as e:
        ServerErrorException(str(e))

from bson import ObjectId
from datetime import datetime
from tortoise import Model, fields


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid object ID")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Business(Model):
    id = fields.IntField(pk=True)
    business_name = fields.CharField(max_length=100, null=False, validate=lambda x: len(x) > 0)
    logo = fields.CharField(max_length=100, default="default.jpg")
    creation_date = fields.DatetimeField(default=datetime.utcnow, null=False)
    last_updated = fields.DatetimeField(default=datetime.utcnow, null=False)
    website = fields.CharField(max_length=100, default="", null=False, validate=lambda x: len(x) > 0)

    class Meta:
        abstract = True


class Product(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, null=False, validate=lambda x: len(x) > 0)
    category = fields.CharField(max_length=100, null=False, validate=lambda x: len(x) > 0)
    price = fields.FloatField(null=False, validate=lambda x: x > 0)
    description = fields.TextField(null=False, validate=lambda x: len(x) > 0)
    ean = fields.CharField(max_length=30, null=False, validate=lambda x: len(x) > 0)
    creation_date = fields.DatetimeField(default=datetime.utcnow, null=False)
    last_updated = fields.DatetimeField(default=datetime.utcnow, null=False)


class ScrapedProduct(Model):
    id = fields.IntField(pk=True)
    asin = fields.CharField(max_length=30, null=False, validate=lambda x: len(x) > 0)
    ean = fields.CharField(max_length=30, null=False, validate=lambda x: len(x) > 0)
    cost = fields.FloatField(null=False, validate=lambda x: x > 0)
    rating = fields.FloatField(null=False, validate=lambda x: 0 <= x <= 5)
    reviews = fields.IntField(null=False, validate=lambda x: x >= 0)
    ROI = fields.FloatField(null=False, validate=lambda x: x >= 0)
    price = fields.FloatField(null=False, validate=lambda x: x > 0)
    profit = fields.FloatField(null=False, validate=lambda x: x >= 0)
    FBA = fields.CharField(max_length=50, null=False, validate=lambda x: len(x) > 0)
    FBM = fields.CharField(max_length=50, null=False, validate=lambda x: len(x) > 0)
    AMZ = fields.CharField(max_length=50, null=False, validate=lambda x: len(x) > 0)
    creation_date = fields.DatetimeField(default=datetime.utcnow, null=False)
    last_updated = fields.DatetimeField(default=datetime.utcnow, null=False)

from datetime import datetime
from tortoise.models import Model
from tortoise import fields
from tortoise.validators import MinLengthValidator, MaxLengthValidator
from tortoise.contrib.pydantic import pydantic_model_creator
from models import Business, Product, ScrapedProduct


class WholesaleBusiness(Business):
    correspondence = fields.CharField(max_length=100, null=False, validators=[MinLengthValidator(5), MaxLengthValidator(100)])
    email = fields.CharField(max_length=100, null=False, validators=[MinLengthValidator(1), MaxLengthValidator(100)])
    phone = fields.CharField(max_length=15, null=False, validators=[MinLengthValidator(8), MaxLengthValidator(20)])
    address = fields.CharField(max_length=100, null=False, validators=[MinLengthValidator(10), MaxLengthValidator(100)])
    category = fields.CharField(max_length=100, null=False, validators=[MinLengthValidator(3), MaxLengthValidator(100)])

    class Meta:
        table_description = "wholesale_business"

    async def validate(self, raise_exception=True):
        if not self.correspondence:
            if raise_exception:
                raise ValueError("Correspondence cannot be empty.")
            else:
                return False
        if not self.email:
            if raise_exception:
                raise ValueError("Email cannot be empty.")
            else:
                return False
        if "@" not in self.email:
            if raise_exception:
                raise ValueError("Invalid email format.")
            else:
                return False
        if not self.phone:
            if raise_exception:
                raise ValueError("Phone number cannot be empty.")
            else:
                return False
        if len(self.phone) != 10:
            if raise_exception:
                raise ValueError("Phone number must be 10 digits long.")
            else:
                return False
        if not self.phone.isdigit():
            if raise_exception:
                raise ValueError("Phone number must only contain digits.")
            else:
                return False
        if not self.address:
            if raise_exception:
                raise ValueError("Address cannot be empty.")
            else:
                return False
        if len(self.address) < 10:
            if raise_exception:
                raise ValueError("Address must be at least 10 characters long.")
            else:
                return False
        if not self.category:
            if raise_exception:
                raise ValueError("Category cannot be empty")
        if len(self.category) < 3:
            if raise_exception:
                raise ValueError("Category must be at least 3 characters long.")
            else:
                return False
        return True


class WholesaleProduct(Product):
    business = fields.ForeignKeyField('models.WholesaleBusiness')

    class Meta:
        table_description = "wholesale_product"

    async def validate(self, raise_exception=True):
        if self.business is None:
            if raise_exception:
                raise ValueError("Product must have a business associated with it.")
            else:
                return False
        return True


class WholesaleScrapedProduct(ScrapedProduct):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200, null=False, validators=[MinLengthValidator(1)])
    price = fields.FloatField(null=False)
    url = fields.CharField(max_length=500, null=False, validators=[MinLengthValidator(1)])
    business = fields.ForeignKeyField('models.WholesaleBusiness', null=True)
    product = fields.ForeignKeyField('models.WholesaleProduct', null=True)

    class Meta:
        table_description = "wholesale_scraped_product"

    async def validate(self, raise_exception=True):
        if not self.name:
            if raise_exception:
                raise ValueError("Name cannot be empty.")
            else:
                return False
        if self.price < 0:
            if raise_exception:
                raise ValueError("Price must be a positive number.")
            else:
                return False
        if not self.url:
            if raise_exception:
                raise ValueError("URL cannot be empty.")
            else:
                return False
        return True


wholesale_business_pydantic = pydantic_model_creator(WholesaleBusiness, name="WholesaleBusiness")
wholesale_business_pydanticIn = pydantic_model_creator(WholesaleBusiness, name="WholesaleBusinessIn",
                                                       exclude_readonly=True, exclude=["creation_date", "last_updated"])


wholesale_product_pydantic = pydantic_model_creator(WholesaleProduct, name="WholesaleProduct")
wholesale_product_pydanticIn = pydantic_model_creator(WholesaleProduct, name="WholesaleProductIn",
                                                      exclude_readonly=True, exclude=["creation_date", "last_updated"])


wholesale_scraped_product_pydantic = pydantic_model_creator(WholesaleScrapedProduct, name="WholesaleScrapedProduct")
wholesale_scraped_product_pydanticIn = pydantic_model_creator(WholesaleScrapedProduct, name="WholesaleScrapedProductIn",
                                                              exclude_readonly=True,
                                                              exclude=["creation_date", "last_updated"])

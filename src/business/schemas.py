from tortoise import fields
from tortoise.validators import MinLengthValidator
from tortoise.contrib.pydantic import pydantic_model_creator
from src.models import Business, Product


class UserBusiness(Business):
    business_description = fields.TextField(null=False, validators=[MinLengthValidator(1)])
    company_number = fields.CharField(max_length=30, null=False, validators=[MinLengthValidator(1)])
    vat_number = fields.CharField(max_length=30, null=False, validators=[MinLengthValidator(1)])
    owner = fields.CharField(max_length=30, null=False, validators=[MinLengthValidator(1)])


class UserProduct(Product):
    cost = fields.FloatField()
    business = fields.ForeignKeyField('models.UserBusiness')

    class Meta:
        table_description = "user_product"

    async def validate(self, raise_exception=True):
        if self.cost < 0:
            if raise_exception:
                raise ValueError("Cost must be a positive number.")
            else:
                return False
        return True


user_business_pydantic = pydantic_model_creator(UserBusiness, name="UserBusiness")
user_business_pydanticIn = pydantic_model_creator(UserBusiness, name="UserBusinessIn", exclude_readonly=True,
                                                  exclude=["owner", "creation_date", "last_updated"])


user_product_pydantic = pydantic_model_creator(UserProduct, name="UserProduct")
user_product_pydanticIn = pydantic_model_creator(UserProduct, name="UserProductIn", exclude_readonly=True,
                                                 exclude=["creation_date", "last_updated"])

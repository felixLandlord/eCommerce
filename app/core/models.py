import pydantic
from tortoise import Model, fields
from pydantic import BaseModel
from datetime import datetime, timezone
from tortoise.contrib.pydantic import pydantic_model_creator


class User(Model):
    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, unique=True, null=False)
    email = fields.CharField(max_length=200, unique=True, null=False)
    password = fields.CharField(max_length=100, null=False)
    is_verified = fields.BooleanField(default=False)
    join_date = fields.DatetimeField(default=datetime.now(timezone.utc))

    

class Business(Model):
    id = fields.IntField(pk=True, index=True)
    business_name = fields.CharField(max_length=20, unique=True, null=False)
    city = fields.CharField(max_length=100, null=False, default="Unspecified")
    region = fields.CharField(max_length=100, null=False, default="Unspecified")
    country = fields.CharField(max_length=100, null=False, default="Unspecified")
    description = fields.TextField(null=True)
    logo = fields.CharField(max_length=200, null=False, default="default.jpg")
    owner = fields.ForeignKeyField('models.User', related_name='businesses')



class Product(Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=100, null=False, index=True)
    category = fields.CharField(max_length=50, index=True, null=False, default="Unspecified")
    description = fields.TextField(null=True)
    original_price = fields.DecimalField(max_digits=12, decimal_places=2)
    new_price = fields.DecimalField(max_digits=12, decimal_places=2)
    percentage_discount = fields.IntField()
    offer_expiration_date = fields.DateField(default=datetime.now(timezone.utc))
    product_image = fields.CharField(max_length=200, null=False, default="defaultProduct.jpg")
    date_published = fields.DatetimeField(default= datetime.now(timezone.utc))
    # quantity = fields.IntField(null=False, default=0)
    business = fields.ForeignKeyField('models.Business', related_name='products')


user_pydantic = pydantic_model_creator(User, name="User", exclude=("is_verified", ))
user_pydanticIn = pydantic_model_creator(User, name="UserIn", exclude_readonly=True, exclude=("is_verified", "join_date"))
user_pydanticOut = pydantic_model_creator(User, name="UserOut", exclude=("password", ))

business_pydantic = pydantic_model_creator(Business, name="Business")
business_pydanticIn = pydantic_model_creator(Business, name="BusinessIn", exclude=("logo", "id"))

product_pydantic = pydantic_model_creator(Product, name="Product")
product_pydanticIn = pydantic_model_creator(Product, name="ProductIn", exclude=("percentage_discount", "id", "product_image", "date_published"))
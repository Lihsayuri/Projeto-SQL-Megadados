from unicodedata import name
from pydantic import BaseModel,Field

class ProductBase(BaseModel):
    name: str = Field(default = "Placeholder", title="O nome do produto", max_length=300, example="Maçã")
    qtd : int = Field(default = 0,  title = "A quantidade do produto", ge=0, description="A quantidade não pode ser negativa", example=4)

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id : int
    owners_id : int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    products: list[Product] = []

    class Config:
        orm_mode = True
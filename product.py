from typing import Union

from fastapi import FastAPI, Body
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

app = FastAPI()

class ProductBase(BaseModel):
    name: str
    price_unit: float
    qtd : int
    is_available: Union[bool, None] = None


mock_database = [{'name' : "banana", 'price_unit': 1.50, 'qtd' : 4 , 'is_available' : True},
                 {'name' : "pêra", 'price_unit': 1.23, 'qtd' : 7 , 'is_available' : True},
                 {'name' : "manga", 'price_unit': 3.50, 'qtd' : 1 , 'is_available' : False},
]


@app.get("/products/{product_id}", status_code=200, response_model = ProductBase, tags=["product"])
async def read_item(product_id: int):
    """
    Procura o produto baseado em seu id de identificação e retorna desse forma:

    {"name":"manga", 

    "price_unit":3.5,

    "qtd":1,
    
    "is_available":false}

    """

    product = mock_database[product_id]
    return product


@app.post("/products/", status_code=201, response_model=ProductBase, tags=["product"])
async def create_item(product: ProductBase = Body(
        example={
            "name": "banana",
            "price_unit": 1.50,
            "qtd": 4,
            "is_available": True,
        })):
    """
    Crie um produto com as seguintes informações abaixo:

    - **name**: nome de cada produto
    - **price_unit**: preço unitário do produto (em reais)
    - **qtd**: quantidade do produto no inventário
    - **is_available**: verdadeiro caso o produto esteja disponível no inventário e falso caso contrário.
    """
    product = product.dict()
    mock_database.append(product)
    return product
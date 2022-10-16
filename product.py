from itertools import product
from typing import Union

from fastapi import FastAPI, Body, HTTPException
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

def product_not_in_db(product_id):
    if product_id >= len(mock_database):
        raise HTTPException(status_code=404, detail="Product not found")


@app.get("/products/{product_id}", status_code=200, response_model = ProductBase, tags=["product"])
async def read_item(product_id: int):
    """
    Procura o produto baseado em seu id de identificação e retorna desse forma:

    {"name":"manga", 

    "price_unit":3.5,

    "qtd":1,
    
    "is_available":false}

    """
    product_not_in_db(product_id)
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

@app.put("/products/{product_id}", tags=["product"])
async def overwrite_item(
    product_id : int, 
    product: ProductBase = Body(
    example={
        "name": "banana",
        "price_unit": 1.50,
        "qtd": 4,
        "is_available": True,
})):

    """
    Sobrescreva um produto com as seguintes informações abaixo:

    - **name**: nome de cada produto
    - **price_unit**: preço unitário do produto (em reais)
    - **qtd**: quantidade do produto no inventário
    - **is_available**: verdadeiro caso o produto esteja disponível no inventário e falso caso contrário.
    """
    product_not_in_db(product_id)
    mock_database[product_id] = product
    return {'product_id': product_id, 'product': product}

@app.delete("/products/{product_id}", tags=["product"])
async def delete_item(product_id : int):
    """
    apaga um produto da base de dados.
    """
    product_not_in_db(product_id)
    product = mock_database[product_id]
    mock_database.pop(product_id)
    return {'removed': product}
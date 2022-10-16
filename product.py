# Importando bibliotecas importantes da FastAPI

from typing import Union
from fastapi import FastAPI, Body, HTTPException, Path, Form
from pydantic import BaseModel,Field
from fastapi.responses import HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()


mock_database = [{'name' : "banana", 'price_unit': 1.50, 'qtd' : 4 , 'is_available' : True},
                 {'name' : "pêra", 'price_unit': 1.23, 'qtd' : 7 , 'is_available' : True},
                 {'name' : "manga", 'price_unit': 3.50, 'qtd' : 1 , 'is_available' : False},
]

# --------------------------------------- Declarando a classe do produto -------------------------------------------------------
class ProductBase(BaseModel):
    name: str = Field(title="O nome do produto", max_length=300, example="Maçã")
    price_unit: float = Field(title = "O preço do produto", gt=0, description="O preço precisa ser maior que 0", example=2.56)
    qtd : int = Field(title = "A quantidade do produto", ge=0, description="A quantidade não pode ser negativa", example=4)
    is_available: Union[bool, None] = Field(title = "Disponibilidade do produto", description = "Se o produto está disponível ou não", example=True)


# ----------------- Declarando função importante para mostrar erros em caso de dado não encontrado -----------------------------
def product_not_in_db(product_id):
    if product_id >= len(mock_database):
        raise HTTPException(status_code=404, detail="Produto não encontrado!")


#  -----------------------------------  Handlers que enviam erros --------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return await request_validation_exception_handler(request, exc)


# --------------------------------------- Implementando o CRUD ------------------------------------------------------------------

@app.get("/", tags=["home page"])
async def main():
    """
    Apenas uma home page com forms para criar um produto
    """
    content = """
<body>
    <form action="/products_/" method="post">

    <label for="name">Nome do produto:</label>
    <input type="text" id="name" name="name"><br><br>

    <label for="price_unit">Preço unitário:</label>
    <input type="txt" id="price_unit" name="price_unit"><br><br>

    <label for="qtd">Quantidade:</label>
    <input type="number" id="qtd" name="qtd"><br><br>

    <label for="is_available">Disponibilidade:</label>
    <input type="text" id="is_available" name="is_available"><br><br>

    <input type="submit">
</body>
    """
    return HTMLResponse(content=content)



@app.post("/products_/", status_code=201, response_model=ProductBase, tags=["product"])
async def create_item(*, name: str = Form(), price_unit : float = Form(), qtd : int = Form(), is_available : str = Form()):
    """
    Crie um produto com as seguintes informações abaixo na home page:

    - **name**: nome de cada produto
    - **price_unit**: preço unitário do produto (em reais)
    - **qtd**: quantidade do produto no inventário
    - **is_available**: verdadeiro caso o produto esteja disponível no inventário e falso caso contrário.
    """
    if is_available == 'True':
        is_available = True
    else:
        is_available = False

    produto = ProductBase(name = name, price_unit = price_unit, qtd = qtd, is_available = is_available)

    product = produto.dict()
    mock_database.append(product)
    return product




@app.get("/products/{product_id}", status_code=200, response_model = ProductBase, tags=["product"])
async def read_item(product_id: int = Path(title="O id do produto que você quer consultar", ge=0)):
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

@app.get("/products/", status_code=200, response_model = list[ProductBase], tags=["product"])
async def read_item():
    """
    Lista todos os produtos e os retorna dessa forma:

    {"name":"manga", 

    "price_unit":3.5,

    "qtd":1,
    
    "is_available":false}

    """
    return mock_database


@app.post("/products/", status_code=201, response_model=ProductBase, tags=["product"])
async def create_item(*, product: ProductBase = Body(
        examples = {
            "normal": {
                "summary": "Um exemplo normal de sucesso",
                "description": "Um exemplo normal de produto que funciona corretamente",
                "value": {
                    "name": "banana",
                    "price_unit": 1.50,
                    "qtd": 4,
                    "is_available": True,
                }
            },
            "convertido": {
                "summary": "Um exemplo com conversão de dados",
                "description": "A FastAPI converte string de preços para números automaticamente e vice-versa",
                "value": {
                    "name" : "banana",
                    "price_unit" : "1.50",
                    "qtd" : 4,
                    "is_available" : True,
                }
            },
            "incorreto" : {
                "summary" : "Um exemplo de dado incorreto",
                "description" : "Nessa situação, quando a tipagem é errada um erro é retornado",
                "value":{
                    "name" : "banana",
                    "price_unit" : "um real e cinquenta centavos",
                    "qtd" : 4,
                    "is_available" : True,
                }
            },

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
    product_id: int = Path(title="O id do produto que você quer editar", ge=0), 
    product: ProductBase = Body(
    examples = {
            "normal": {
                "summary": "Um exemplo normal de sucesso",
                "description": "Um exemplo normal de produto que funciona corretamente",
                "value": {
                    "name": "banana",
                    "price_unit": 1.50,
                    "qtd": 4,
                    "is_available": True,
                }
            },
            "convertido": {
                "summary": "Um exemplo com conversão de dados",
                "description": "A FastAPI converte string de preços para números automaticamente e vice-versa",
                "value": {
                    "name" : "banana",
                    "price_unit" : "1.50",
                    "qtd" : 4,
                    "is_available" : True,
                }
            },
            "incorreto" : {
                "summary" : "Um exemplo de dado incorreto",
                "description" : "Nessa situação, quando a tipagem é errada um erro é retornado",
                "value":{
                    "name" : "banana",
                    "price_unit" : "um real e cinquenta centavos",
                    "qtd" : 4,
                    "is_available" : True,
                }
            },
    })):

    """
    Atualize as informações de um produto com as seguintes informações abaixo:

    - **name**: nome de cada produto
    - **price_unit**: preço unitário do produto (em reais)
    - **qtd**: quantidade do produto no inventário
    - **is_available**: verdadeiro caso o produto esteja disponível no inventário e falso caso contrário.
    """
    product_not_in_db(product_id)
    mock_database[product_id] = product
    return {'product_id': product_id, 'product': product}

@app.delete("/products/{product_id}", tags=["product"])
async def delete_item(product_id: int = Path(title="O id do produto que você quer deletar", ge=0)):
    """
    apaga um produto da base de dados.
    """
    product_not_in_db(product_id)
    product = mock_database[product_id]
    mock_database.pop(product_id)
    return {'removed': product}
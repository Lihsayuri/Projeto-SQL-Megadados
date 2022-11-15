# Importando bibliotecas importantes da FastAPI

from email.policy import default
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
from fastapi.encoders import jsonable_encoder

app = FastAPI()


mock_database = [{'id' : 1, 'name' : "banana", 'qtd' : 4},
                 {'id': 2, 'name' : "pêra", 'qtd' : 7},
                 {'id': 3, 'name' : "manga", 'qtd' : 1}]

# --------------------------------------- Declarando a classe do produto -------------------------------------------------------
class ProductUpdate(BaseModel):
    name: str = Field(default = "Placeholder", title="O nome do produto", max_length=300, example="Maçã")
    qtd : int = Field(default = 0,  title = "A quantidade do produto", ge=0, description="A quantidade não pode ser negativa", example=4)

class ProductBase(ProductUpdate):
    id : int = Field(title = "Id do produto", description = "Identificador do produto", ge = 1)
    # name: str = Field(default = "Placeholder", title="O nome do produto", max_length=300, example="Maçã")
    # qtd : int = Field(default = 0,  title = "A quantidade do produto", ge=0, description="A quantidade não pode ser negativa", example=4)

# ----------------- Declarando função importante para mostrar erros em caso de dado não encontrado -----------------------------
def product_not_in_db(product_id):
    if product_id not in [product['id'] for product in mock_database]:
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
    Apenas uma home page com gosto de macarrão
    """
    content = """
<body>
    <h1>Buon giorno mondo!</h1>
</body>
    """
    return HTMLResponse(content=content)



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
    for product in mock_database:
        if product['id'] == product_id:
            produto = product

    return produto

@app.get("/products/", status_code=200, response_model = list[ProductBase], tags=["product"])
async def read_item():
    """
    Lista todos os produtos e os retorna dessa forma:

    {"name":"manga", 

    "qtd":1}
    """
    return mock_database


@app.post("/products/", status_code=201, response_model=ProductBase, tags=["product"])
async def create_item(*, product: ProductBase = Body(
        examples = {
            "normal": {
                "summary": "Um exemplo normal de sucesso",
                "description": "Um exemplo normal de produto que funciona corretamente",
                "value": {
                    "id": 1,
                    "name": "banana",
                    "qtd": 4,
                }
            },
            "convertido": {
                "summary": "Um exemplo com conversão de dados",
                "description": "A FastAPI converte string de quantidade para números automaticamente e vice-versa",
                "value": {
                    "id": "1",
                    "name" : "banana",
                    "qtd" : "4"
                }
            },
            "incorreto" : {
                "summary" : "Um exemplo de dado incorreto",
                "description" : "Nessa situação, quando a tipagem é errada um erro é retornado",
                "value":{
                    "id" : "um",
                    "name" : "banana",
                    "qtd" : "quatro"
                }
            },

        })):
    """
    Crie um produto com as seguintes informações abaixo:

    - **id**: id de cada produto
    - **name**: nome de cada produto
    - **qtd**: quantidade do produto no inventário
    """
    product = product.dict()
    mock_database.append(product)
    return product

@app.put("/products/{product_id}", tags=["product"])
async def overwrite_item(
    product_id: int = Path(title="O id do produto que você quer editar", ge=0), 
    product: ProductUpdate = Body(
        examples = {
            "normal": {
                "summary": "Um exemplo normal de sucesso",
                "description": "Um exemplo normal de produto que funciona corretamente",
                "value": {
                    "name": "banana",
                    "qtd": 4,
                }
            },
            "convertido": {
                "summary": "Um exemplo com conversão de dados",
                "description": "A FastAPI converte string de quantidade para números automaticamente e vice-versa",
                "value": {
                    "name" : "banana",
                    "qtd" : "4"
                }
            },
            "incorreto" : {
                "summary" : "Um exemplo de dado incorreto",
                "description" : "Nessa situação, quando a tipagem é errada um erro é retornado",
                "value":{
                    "name" : "banana",
                    "qtd" : "quatro"
                }
            },

        })):

    """
    Atualize totalmente as informações de um produto com as seguintes informações abaixo:

    - **id**: id de cada produto (mas você não pode atualizá-lo. O id a ser considerado é o que
    escreve no campo product_id separadamente)
    - **name**: nome de cada produto
    - **qtd**: quantidade do produto no inventário
    """
    product_not_in_db(product_id)
    for produto in mock_database:
        if produto['id'] == product_id:
            produto['name'] = product.name
            produto['qtd'] = product.qtd        
            
    return {'product_id': product_id, 'product': product}

@app.patch("/products/{product_id}", response_model=ProductBase, tags=["product"])
async def update_item(
    product_id: int, 
    product: ProductUpdate = Body(examples = {
        "nome": {
            "summary" : "Um exemplo modificando apenas o nome",
            "value" :{
                "name" : "maçã"
            }
        },
        "quantidade" : {
            "summary" : "Um exemplo modificando apenas a quantidade",
            "value" : {
                "qtd" : 0
            }
        }
        })):
    """
    Atualize parcialmente as informações de um produto com as seguintes informações abaixo:
    
    - **id**: id de cada produto
    - **name**: nome de cada produto
    - **qtd**: quantidade do produto no inventário
    """


    for produto in mock_database:
        if produto['id'] == product_id:
            produto_escolhido = produto

    stored_product_data = produto_escolhido
    stored_product_model = ProductUpdate(**stored_product_data)
    update_data = product.dict(exclude_unset=True)
    update_data['id'] = product_id
    updated_product = stored_product_model.copy(update=update_data)
    temp_product =  ProductBase(id=product_id, name= updated_product.name, qtd = updated_product.qtd)

    for i in range(len(mock_database)):
        if mock_database[i]['id'] == product_id:
            mock_database[i] = temp_product.dict()

    return temp_product

@app.delete("/products/{product_id}", tags=["product"])
async def delete_item(product_id: int = Path(title="O id do produto que você quer deletar", ge=0)):
    """
    Apaga um produto da base de dados.
    """
    product_not_in_db(product_id)

    for produto in mock_database:
        if produto['id'] == product_id:
            mock_database.remove(produto)

    return {'Produto removido com sucesso. Antigo id': product_id}
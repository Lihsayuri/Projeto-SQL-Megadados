# Importando bibliotecas importantes da FastAPI

from email.policy import default
from re import M
from typing import Union
from fastapi import FastAPI, Body, HTTPException, Path, Form, Response, Request, Depends
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


from sqlalchemy.orm import Session
import crud, models, schemas
# from Schemas import ProductCreate
from database import SessionLocal, engine

from dotenv import load_dotenv

#load_dotenv('.env')

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# ----------------- Declarando função importante para mostrar erros em caso de dado não encontrado -----------------------------
# Confere se o id do produto está no banco de dados e retorna um erro caso não seja encontrado
def product_not_in_db(db : Session, product_id: int):
    if crud.get_product(db, product_id) is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

def mov_not_in_db(db : Session, id_mov: int):
    if crud.get_movimentacao(db, id_mov) is None:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada")

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



#-------------------------------------------- CRUD de produtos ---------------------------------------------------------------



@app.get("/products/{product_id}", status_code=200, response_model = schemas.Estoque, tags=["product"])
async def read_item(Session = Depends(get_db), product_id: int = Path(title="O id do produto que você quer consultar", ge=0)):
    """
    Procura o produto baseado em seu id de identificação e retorna desse forma:

    {
        "id": 8,
        "name": "manga",
        "qtd": 0
    }

    """
    product_not_in_db(db = Session, product_id = product_id)
    product = crud.get_product(db = Session, product_id = product_id)
    return product



@app.get("/products/", status_code=200, response_model = list[schemas.Estoque], tags=["product"])
async def read_item(Session = Depends(get_db)):
    """
    Lista todos os produtos e os retorna dessa forma:

    [
        {
            "id": 5,
            "name": "banana",
            "qtd": 0
        },
        {
            "id": 6,
            "name": "carambola",
            "qtd": 0
        },
        {
            "id": 8,
            "name": "manga",
            "qtd": 0
        },
        {
            "id": 7,
            "name": "uva",
            "qtd": 0
        }
    ]
    """

    products = crud.get_products(db=Session)
    return products


@app.post("/products/", status_code=201, response_model=schemas.Estoque, tags=["product"])
async def create_product(Session = Depends(get_db) , product: schemas.EstoqueCreate = Body(
        examples = {
            "normal": {
                "summary": "Um exemplo normal de sucesso",
                "description": "Um exemplo normal de produto que funciona corretamente",
                "value": {
                    "name": "banana"
                }
            },
            "convertido": {
                "summary": "Um exemplo com conversão de dados",
                "description": "A FastAPI converte string de quantidade para números automaticamente e vice-versa",
                "value": {
                    "name" : "banana",
                }
            },
            "incorreto" : {
                "summary" : "Um exemplo de dado incorreto",
                "description" : "Nessa situação, quando a tipagem é errada um erro é retornado",
                "value":{
                    "name" : "banana",
                }
            },

        })):
    """
    Crie um produto com as seguintes informações abaixo:

    - **user_id**: id do usuário que criou o produto
    - **name**: nome de cada produto
    - **qtd**: quantidade do produto no inventário
    """
    db_product = crud.create_product(db=Session, product=product)
    return db_product


@app.delete("/products/{product_id}", status_code=200, response_model=schemas.Estoque, tags=["product"])
async def delete_item(Session = Depends(get_db),product_id: int = Path(title="O id do produto que você quer deletar", ge=0)):
    """
    Apaga um produto da base de dados.

    """
    product_not_in_db(Session, product_id)
    return crud.delete_product(db=Session, product_id=product_id)
 


# Atualiza apenas o nome do produto
@app.put("/products/{product_id}", tags=["product"])
async def overwrite_item(
    Session = Depends(get_db),
    product_id: int = Path(title="O id do produto que você quer editar", ge=0), 
    product: schemas.EstoqueCreate = Body(
        examples = {
            "normal": {
                "summary": "Um exemplo normal de sucesso",
                "description": "Um exemplo normal de produto que funciona corretamente",
                "value": {
                    "name": "banana",
                }
            },
        })):

    """
    Atualize totalmente as informações de um produto com as seguintes informações abaixo:

    - **product_id**: id do usuário que criou o produto
    - **name**: nome do produto que você quer editar

    """
    product_not_in_db(Session , product_id)
    db_product = crud.update_product_nome(db=Session, product=product, product_id=product_id)

    return db_product



#  # -------------------------------------- CRUD de usuários --------------------------------------------------------


@app.get("/movimentacao/{id_mov}", status_code=200, response_model = schemas.Movimentacao, tags=["movimentacao"])
async def read_item(Session = Depends(get_db), id_mov: int = Path(title="O id da movimentação que você quer consultar", ge=0)):
    """
    Procura a movimentação baseado em seu id de identificação e retorna desse forma:

        {
        "id_mov": 1,
        "qtd": 5,
        "product_id": 5
        }
    """
    mov_not_in_db(db = Session, id_mov = id_mov)
    mov = crud.get_movimentacao(db = Session, movimentacao_id = id_mov)
    return mov


@app.get("/movimentacao/", status_code=200, response_model = list[schemas.Movimentacao], tags=["movimentacao"])
async def read_item(Session = Depends(get_db)):
    """
    Lista todos os usuários e os retorna dessa forma:

    [

        {
            "id_mov": 1,
            "qtd": 5,
            "product_id": 5
        },
        {
            "id_mov": 2,
            "qtd": -2,
            "product_id": 5
        },
        {
            "id_mov": 3,
            "qtd": 2,
            "product_id": 6
        }
        
    ]

    """

    movs = crud.get_movimentacao_all(db=Session)
    return movs


@app.post("/products/{product_id}", status_code=201, response_model= schemas.Movimentacao, tags=["movimentacao"])
async def create_movimentacao(db : Session = Depends(get_db) , 
mov: schemas.MovimentacaoCreate = Body(
        examples = {
            "normal": {
                "summary": "Um exemplo normal de sucesso",
                "description": "Um exemplo normal de usuário que funciona corretamente",
                "value": {
                    "product_id": 5,
                    "qtd": 5,
                }
            }
        })):
    """
    Crie uma movimentação com as seguintes informações abaixo:

    - **product_id**: id do produto que você quer movimentar
    - **qtd**: quantidade do produto que você quer alterar
    """

    product_not_in_db(db, mov.product_id)
    return crud.create_movimentacao(db=db, movimentacao=mov)
 

 
# @app.delete("/users/{user_id}", tags=["user"])
# async def delete_item(Session = Depends(get_db),user_id: int = Path(title="O id do usuário que você quer deletar", ge=0)):
#     """
#     Apaga um usuário da base de dados.
#     """
#     user_not_in_db(Session, user_id)
#     return crud.delete_user(db=Session, user_id=user_id)
 



# @app.patch("/products/{product_id}", response_model=ProductBase, tags=["product"])
# async def update_item(
#     product_id: int, 
#     product: ProductBase = Body(examples = {
#         "nome": {
#             "summary" : "Um exemplo modificando apenas o nome",
#             "value" :{
#                 "name" : "maçã"
#             }
#         },
#         "quantidade" : {
#             "summary" : "Um exemplo modificando apenas a quantidade",
#             "value" : {
#                 "qtd" : 0
#             }
#         }
#         })):
#     """
#     Atualize parcialmente as informações de um produto com as seguintes informações abaixo:

#     - **name**: nome de cada produto
#     - **qtd**: quantidade do produto no inventário
#     """
#     stored_product_data = mock_database[product_id]
#     stored_product_model = ProductBase(**stored_product_data)
#     update_data = product.dict(exclude_unset=True)
#     updated_product = stored_product_model.copy(update=update_data)
#     mock_database[product_id] = jsonable_encoder(updated_product)
#     return updated_product


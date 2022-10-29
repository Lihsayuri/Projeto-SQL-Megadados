# Importando bibliotecas importantes da FastAPI

from email.policy import default
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

def user_not_in_db(db : Session, user_id: int):
    if crud.get_user(db, user_id) is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

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



@app.get("/products/{product_id}", status_code=200, response_model = schemas.Product, tags=["product"])
async def read_item(Session = Depends(get_db), product_id: int = Path(title="O id do produto que você quer consultar", ge=0)):
    """
    Procura o produto baseado em seu id de identificação e retorna desse forma:

    {

        "name": "banana",
        "qtd": 4,
        "id": 1,
        "user_id": 1
    
    }

    """
    product_not_in_db(db = Session, product_id = product_id)
    product = crud.get_product(db = Session, product_id = product_id)
    return product



@app.get("/products/", status_code=200, response_model = list[schemas.Product], tags=["product"])
async def read_item(Session = Depends(get_db)):
    """
    Lista todos os produtos e os retorna dessa forma:

    [

        {

            "name": "banana",
            "qtd": 4,
            "id": 1,
            "user_id": 1

        },

        {
            "name": "manga",
            "qtd": 4,
            "id": 2,
            "user_id": 1

        }
    ]
    """

    products = crud.get_products(db=Session)
    return products


@app.post("/products/", status_code=201, response_model=schemas.Product, tags=["product"])
async def create_product(user_id: int, Session = Depends(get_db) , product: schemas.ProductCreate = Body(
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
                    "qtd" : "4",
                }
            },
            "incorreto" : {
                "summary" : "Um exemplo de dado incorreto",
                "description" : "Nessa situação, quando a tipagem é errada um erro é retornado",
                "value":{
                    "name" : "banana",
                    "qtd" : "quatro",
                }
            },

        })):
    """
    Crie um produto com as seguintes informações abaixo:

    - **user_id**: id do usuário que criou o produto
    - **name**: nome de cada produto
    - **qtd**: quantidade do produto no inventário
    """
    db_product = crud.create_product(db=Session, product=product, user_id = user_id)
    return db_product




@app.put("/products/user{user_id}/{product_id}", tags=["product"])
async def overwrite_item(
    Session = Depends(get_db),
    product_id: int = Path(title="O id do produto que você quer editar", ge=0), 
    user_id: int = Path(title="O id do usuário que quer editar o produto", ge=0),
    product: schemas.ProductCreate = Body(
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

    - **name**: nome de cada produto
    - **qtd**: quantidade do produto no inventário
    - **user_id**: id do usuário que criou o produto

    Observação: O id do usuário não pode ser alterado, pois uma vez que o produto foi criado, ele pertence a um usuário específico.

    """
    product_not_in_db(Session , product_id)
    db_product = crud.update_product(db=Session, product=product, product_id=product_id)

    return db_product


@app.delete("/products/{product_id}", tags=["product"])
async def delete_item(Session = Depends(get_db),product_id: int = Path(title="O id do produto que você quer deletar", ge=0)):
    """
    Apaga um produto da base de dados.
    """
    product_not_in_db(Session, product_id)
    return crud.delete_product(db=Session, product_id=product_id)
 

 # -------------------------------------- CRUD de usuários --------------------------------------------------------


@app.get("/user/{user_id}", status_code=200, response_model = schemas.User, tags=["user"])
async def read_item(Session = Depends(get_db), user_id: int = Path(title="O id do usuário que você quer consultar", ge=0)):
    """
    Procura o usuário baseado em seu id de identificação e retorna desse forma:

    {

        "email": "max_verstappen@hotmail.com",
        "first_name": "max",
        "last_name": "verstappen",
        "id": 1,
        "products": [
            {
            "name": "banana",
            "qtd": 4,
            "id": 1,
            "user_id": 1
            },
            {
            "name": "manga",
            "qtd": 4,
            "id": 2,
            "user_id": 1
            }
    }

    """
    user_not_in_db(db = Session, user_id = user_id)
    user = crud.get_user(db = Session, user_id = user_id)
    return user



@app.get("/users/", status_code=200, response_model = list[schemas.User], tags=["user"])
async def read_item(Session = Depends(get_db)):
    """
    Lista todos os usuários e os retorna dessa forma:

[
    {

        "email": "max_verstappen@hotmail.com",
        "first_name": "max",
        "last_name": "verstappen",
        "id": 1,
        "products": [
        {
            "name": "banana",
            "qtd": 4,
            "id": 1,
            "user_id": 1
        },
        {
            "name": "manga",
            "qtd": 4,
            "id": 2,
            "user_id": 1
        }
        ]
    },

    {
        "email": "lando_norris@hotmail.com",
        "first_name": "lando",
        "last_name": "norris",
        "id": 2,
        "products": []
    },
  ]

    """

    users = crud.get_users(db=Session)
    return users


@app.post("/users/", status_code=201, response_model= schemas.User, tags=["user"])
async def create_user(db : Session = Depends(get_db) , user: schemas.UserCreate = Body(
        examples = {
            "normal": {
                "summary": "Um exemplo normal de sucesso",
                "description": "Um exemplo normal de usuário que funciona corretamente",
                "value": {
                    "email": "max_verstappen@hotmail.com",
                    "first_name": "max",
                    "last_name": "verstappen",
                    "password" : "simplylovely",
                }
            }
        })):
    """
    Crie um usuário com as seguintes informações abaixo:

    - **email**: email do usuário
    - **first_name**: nome de cada usuário
    - **last_name**: sobrenome de cada usuário
    - **password**: senha de cada usuário
    """


    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email já está registrado")


    return crud.create_user(db=db, user=user)
 

 
@app.delete("/users/{user_id}", tags=["user"])
async def delete_item(Session = Depends(get_db),user_id: int = Path(title="O id do usuário que você quer deletar", ge=0)):
    """
    Apaga um usuário da base de dados.
    """
    user_not_in_db(Session, user_id)
    return crud.delete_user(db=Session, user_id=user_id)
 



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


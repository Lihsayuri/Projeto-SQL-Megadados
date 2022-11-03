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
    Apenas uma home page com informações resumidas sobre modo de uso da API.
    Para mais detalhes, confira a documentação no /docs.

    """
    content = """
<body>
    <h1> Buon giorno mondo! :) </h1>
    <p> Com a nossa API você poderá gerenciar um estoque. Para isso temos duas tabelas que você pode controlar: 
    a tabela de Estoque e a tabela de Movimentações</p>
    <ul> Na tabela de <b>Estoque</b> você poderá: 
        <li>Criar produtos (apenas o nome, seu id (este sendo opcional) e disponibilidade (que por padrão na criação é True)</li>
        <li> Atualizar essas informações para o produto </li>
        <li> Consultar os produtos sobre: seu id, nome, quantidade e disponibilidade </li>
        <li> E deletar o produto e todas suas movimentações do banco de dados [tome cuidado com isso] </li>
    </ul>
    <ul> Na tabela de <b>Movimentação</b> você poderá: 
        <li> Criar movimentações (id, id do produto a ser referenciado e a quantidade a ser somada ou subtraida)</li>
        <li> Atualizar essas informações caso você tenha errado </li>
        <li> Consultar as movimentações </li>
        <li> E deletar a movimentação feita </li>
    </ul>

    <a href="http://127.0.0.1:8000/docs">Link para documentação e teste da API</a>
    

    <p> By: Bernardo Cunha Capoferri e Lívia Sayuri Makuta. </p>

</body>
    """
    return HTMLResponse(content=content)



#-------------------------------------------- CRUD DE ESTOQUE ---------------------------------------------------------------



@app.get("/products/{product_id}", status_code=200, response_model = schemas.Estoque, tags=["product"])
async def read_item(Session = Depends(get_db), product_id: int = Path(title="O id do produto que você quer consultar", ge=0)):
    """
    Procura o produto baseado em seu id de identificação e retorna desse forma:

    {

        "id": 8,
        "name": "manga",
        "qtd": 0,
        "available": true

    }

    """
    product_not_in_db(db = Session, product_id = product_id)
    product = crud.get_product(db = Session, product_id = product_id)
    return product



@app.get("/products/", status_code=200, response_model = list[schemas.Estoque], tags=["product"])
async def read_items(Session = Depends(get_db)):
    """
    Lista todos os produtos e os retorna dessa forma:

    [

        {
            "id": 5,
            "name": "banana",
            "qtd": 0,
            "available": true
        },
        {
            "id": 6,
            "name": "carambola",
            "qtd": 0,
            "available": true
        },
        {
            "id": 8,
            "name": "manga",
            "qtd": 0,
            "available": false
        },
        {
            "id": 7,
            "name": "uva",
            "qtd": 0
            "available": true
        }

    ]
    """

    products = crud.get_products(db=Session)
    return products


@app.post("/products/", status_code=201, response_model=schemas.Estoque, tags=["product"])
async def create_product(Session = Depends(get_db) , product: schemas.EstoqueCreate = Body(
        examples = {
            "normal sem id": {
                "summary": "Um exemplo normal de sucesso (sem id)",
                "description": "Um exemplo normal de produto que funciona corretamente (sem precisar colocar o id)",
                "value": {
                    "name": "banana"
                }
            },
            "normal com id": {
                "summary": "Um exemplo normal de sucesso (com id)",
                "description": "Um exemplo normal de produto que funciona corretamente (opcionalmente o usuário pode escolher o id)",
                "value": {
                    "id" : 1,
                    "name": "banana"
                }
            },
            "incorreto" : {
                "summary" : "Um exemplo de dado incorreto",
                "description" : "Nessa situação, quando a tipagem é errada um erro é retornado",
                "value":{
                    "id" : "um",
                    "name" : "banana"
                }
            },

        })):
    """
    Crie um produto com as seguintes informações abaixo:

    - **id**: id do produto (que pode ser escolhido ou que será gerado automaticamente de maneira sequencial).
    - **name**: nome de cada produto.
    - **qtd**: quantidade do produto no inventário.
    - **available**: disponibilidade do produto no inventário.

    **Obs:** quando criado entende-se que o produto está disponível no inventário. Caso queira alterar essa informação, use o método PUT.
    Assim, basta realizar um update no produto e alterar o valor de available para false.


    """
    db_product = crud.create_product(db=Session, product=product)
    return db_product


@app.put("/products/{product_id}", tags=["product"], status_code=200, response_model=schemas.Estoque)
async def overwrite_item(
    Session = Depends(get_db),
    product_id: int = Path(title="O id do produto que você quer editar", ge=0), 
    product: schemas.EstoqueUpdate = Body(
        examples = {
            "normal sem id": {
                "summary": "Um exemplo normal de sucesso",
                "description": "Um exemplo normal de produto que funciona corretamente",
                "value": {
                    "name": "banana",
                    "available": False
                }
            },
        })):

    """
    Atualize totalmente as informações de um produto com as seguintes informações abaixo:

    - **name**: nome do produto que você quer editar
    - **available**: se o produto está disponível ou não

    **Importante:** a disponibilidade do produto é entendida como : a empresa possui um estoque e ainda trabalha
    com determinado produto ou não. Porém, ainda que esse produto esteja indisponível, **é possível** fazer movimentações 
    com ele, isso porque pode ser que a empresa deixou de comprar esse produto, mas ainda tenha no estoque. Assim, caso queira
    zerar a quantidade no estoque de um produto, é possível fazer movimentações para alterar a quantidade do produto para 0. 

    Ainda, um método **mais radical** é deletar o produto, mas isso **não é recomendado**, pois pode ser que a empresa
    queira voltar a trabalhar com esse produto no futuro e queira saber as movimentações que foram feitas anteriormente
    com ele.

    """
    product_not_in_db(Session , product_id)
    db_product = crud.update_product_nome(db=Session, product=product, product_id=product_id)

    return db_product


@app.delete("/products/{product_id}", status_code=200, response_model=schemas.Estoque, tags=["product"])
async def delete_item(Session = Depends(get_db),product_id: int = Path(title="O id do produto que você quer deletar", ge=0)):
    """
    Apaga um produto da base de dados e todas as movimentações relacionadas a ele. 

    **Atenção:** essa ação **não pode ser desfeita**, tome cuidado ao usar esse método.	

    """
    product_not_in_db(Session, product_id)
    return crud.delete_product(db=Session, product_id=product_id)




#  # -------------------------------------- CRUD DE MOVIMENTAÇÃO --------------------------------------------------------


@app.get("/movimentacao/{id_mov}", status_code=200, response_model = schemas.Movimentacao, tags=["movimentacao"])
async def read_movimentacao(Session = Depends(get_db), id_mov: int = Path(title="O id da movimentação que você quer consultar", ge=0)):
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
async def read_movimentacoes(Session = Depends(get_db)):
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


@app.post("/movimentacao/{product_id}", status_code=201, response_model= schemas.Movimentacao, tags=["movimentacao"])
async def create_movimentacao(db : Session = Depends(get_db) , 
mov: schemas.MovimentacaoCreate = Body(
        examples = {
            "normal sem id": {
                "summary": "Um exemplo normal de sucesso (sem id)",
                "description": "Um exemplo normal de movimentação que funciona corretamente (sem id)",
                "value": {
                    "product_id": 5,
                    "qtd": 5,
                }
            },
            "normal com id": {
                "summary": "Um exemplo normal de sucesso",
                "description": "Um exemplo normal de movimentação que funciona corretamente (com id)",
                "value": {
                    "id_mov" : 1,
                    "product_id": 5,
                    "qtd": 5,
                }
            },
            "incorreto": {
                "summary": "Um exemplo incorreto de movimentação",
                "description": "Um exemplo com tipagem incorreta de movimentação que não funciona",
                "value": {
                    "id_mov" : "um",
                    "product_id": "cinco",
                    "qtd": "cinco",
                }
            }
        })):
    """
    Crie uma movimentação com as seguintes informações abaixo:

    - **id_mov**: id da movimentação que você quer criar (opcional)
    - **product_id**: id do produto que você quer movimentar
    - **qtd**: quantidade do produto que você quer alterar

    """

    product_not_in_db(db, mov.product_id)
    return crud.create_movimentacao(db=db, movimentacao=mov)
 

 
@app.delete("/movimentacao/{mov_id}", status_code=200, response_model= schemas.Movimentacao, tags=["movimentacao"])
async def delete_movimentacao(Session = Depends(get_db), mov_id: int = Path(title="O id da movimentação que você quer deletar", ge=0)):
    """
    Apaga uma movimentação da base de dados e automaticamente atualiza o estoque.

    **Atenção:** essa ação **não pode ser desfeita**, tome cuidado ao usar esse método.	

    """
    mov_not_in_db(Session, mov_id)
    return crud.delete_movimentacao(db=Session, movimentacao_id = mov_id)
 

@app.put("/movimentacao/{mov_id}", status_code = 200, response_model= schemas.Movimentacao, tags=["movimentacao"])
async def overwrite_movimentacao(
    Session = Depends(get_db),
    mov_id: int = Path(title="O id da movimentação que você quer editar", ge=0), 
    mov: schemas.MovimentacaoCreate = Body(
        examples = {
            "normal": {
                "summary": "Um exemplo normal de sucesso",
                "description": "Um exemplo normal de atualização que funciona corretamente",
                "value": {
                    "product_id": 5,
                    "qtd": 5,
                }
            },
            "incorreto": {
                "summary": "Um exemplo incorreto de atualização",
                "description": "Um exemplo incorreto de atualização que não funciona",
                "value": {
                    "product_id": "cinco",
                    "qtd": "cinco",
                }
            }
        })):

    """
    Atualize totalmente as informações de uma movimentação com as seguintes informações abaixo:

    - **id_mov**: id da movimentação
    - **qtd**: quantidade nova da movimentação
    - **product_id**: o id do produto que você quer alterar na movimentação

    """
    mov_not_in_db(Session , mov_id)
    product_not_in_db(Session, mov.product_id)
    db_mov = crud.update_movimentacao(db=Session, movimentacao_id= mov_id, movimentacao= mov)

    return db_mov


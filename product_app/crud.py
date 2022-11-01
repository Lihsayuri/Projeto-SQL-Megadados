from itertools import product
from tkinter import CASCADE
from sqlalchemy.orm import Session

import models, schemas


def get_product(db: Session, product_id: int):
    return db.query(models.Estoque).filter(models.Estoque.id == product_id).first()

def get_products(db: Session):
    return db.query(models.Estoque).all()

# faça função para criar produto no banco de dados no mysql
def create_product(db: Session, product: schemas.EstoqueCreate):
    # cria produto no banco de dados e retorna o produto criado
    db_product = models.Estoque(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# função para deletar produto no banco de dados no mysql
def delete_product(db: Session, product_id: int):
    # tenta deletar o producto e movimentação do banco de dados se der erradp, faz rollback
    db_product = db.query(models.Estoque).filter(models.Estoque.id == product_id).first()
    # Guardar esse db_product em uma variável para retornar depois no formato de Estoque

    try:
        db.delete(db_product)
        db.commit()
    except:
        db.rollback()

    # Retorne o produto deletado
    return db_product

def update_product_nome(db: Session, product: schemas.EstoqueCreate, product_id: int):
    db_product = db.query(models.Estoque).filter(models.Estoque.id == product_id).first()
    db_product.name = product.name
    try:
        db.commit()
    except:
        db.rollback()
    db.refresh(db_product)
    return db_product


# função que cria uma movimentação no banco de dados
def create_movimentacao(db: Session, movimentacao: schemas.MovimentacaoCreate):
    # cria movimentação no banco de dados e retorna a movimentação criada
    db_movimentacao = models.Movimentacao(**movimentacao.dict())
    db.add(db_movimentacao)
    try:
        update_product(db, movimentacao)
        db.commit()
    except:
        db.rollback()
    db.refresh(db_movimentacao)
    return db_movimentacao

# função que atualiza a quantidade de um produto no estoque com base na movimentação
def update_product(db: Session, movimentacao: schemas.MovimentacaoCreate):
    db_product = db.query(models.Estoque).filter(models.Estoque.id == movimentacao.product_id).first()
    db_product.qtd = db_product.qtd + movimentacao.qtd
    try:
        db.commit()
    except:
        db.rollback()
    db.refresh(db_product)
    return db_product


def get_movimentacao(db: Session, movimentacao_id: int):
    return db.query(models.Movimentacao).filter(models.Movimentacao.id_mov == movimentacao_id).first()


def get_movimentacao_all(db: Session):
    return db.query(models.Movimentacao).all()

# def get_movimentacao(db: Session, id_mov: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()


# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()


# def get_users(db: Session):
#     return db.query(models.User).all()


# def create_user(db: Session, user: schemas.UserCreate):
#     fake_hashed_password = user.password + "notreallyhashed"
#     db_user = models.User(email=user.email, first_name=user.first_name, last_name=user.last_name, hashed_password=fake_hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


# def delete_user(db: Session, user_id: int):
#     db_user = db.query(models.User).filter(models.User.id == user_id).first()
#     db.delete(db_user)
#     db.commit()
#     return db_user


# def create_product(db: Session, product: schemas.ProductCreate):
#     # cria produto no banco de dados e retorna o produto criado
#     db_product = models.Product(**product.dict())
#     db.add(db_product)
#     db.commit()
#     db.refresh(db_product)
#     return db_product

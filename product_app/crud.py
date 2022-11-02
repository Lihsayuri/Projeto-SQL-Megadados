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
    try:
        db.add(db_product)
        db.commit()
    except:
        db.rollback()
    db.refresh(db_product)
    return db_product

# função para deletar produto no banco de dados no mysql
def delete_product(db: Session, product_id: int):
    db_product = db.query(models.Estoque).filter(models.Estoque.id == product_id).first()

    try:
        db.delete(db_product)
        db.commit()
    except:
        db.rollback()

    # Retorne o produto deletado
    return db_product

def update_product_nome(db: Session, product: schemas.EstoqueCreate, product_id: int):
    db_product = db.query(models.Estoque).filter(models.Estoque.id == product_id).first()
    try:
        db_product.name = product.name
        db.commit()
    except:
        db.rollback()
    db.refresh(db_product)
    return db_product

# função que atualiza a quantidade de um produto no estoque com base na movimentação
def update_product(db: Session, movimentacao: schemas.MovimentacaoCreate):
    db_product = db.query(models.Estoque).filter(models.Estoque.id == movimentacao.product_id).first()
    try:
        db_product.qtd = db_product.qtd + movimentacao.qtd
        db.commit()
    except:
        db.rollback()
    db.refresh(db_product)
    return db_product

# função que cria uma movimentação no banco de dados
def create_movimentacao(db: Session, movimentacao: schemas.MovimentacaoCreate):
    # cria movimentação no banco de dados e retorna a movimentação criada
    db_movimentacao = models.Movimentacao(**movimentacao.dict())
    try:
        db.add(db_movimentacao)
        update_product(db, movimentacao)
        db.commit()
    except:
        db.rollback()
    db.refresh(db_movimentacao)
    return db_movimentacao

def get_movimentacao(db: Session, movimentacao_id: int):
    return db.query(models.Movimentacao).filter(models.Movimentacao.id_mov == movimentacao_id).first()

def get_movimentacao_all(db: Session):
    return db.query(models.Movimentacao).all()

def delete_movimentacao(db: Session, movimentacao_id: int):
    db_movimentacao = db.query(models.Movimentacao).filter(models.Movimentacao.id_mov == movimentacao_id).first()
    db_product = db.query(models.Estoque).filter(models.Estoque.id == db_movimentacao.product_id).first()
    try:
        db_product.qtd -= db_movimentacao.qtd
        db.delete(db_movimentacao)
        db.commit()
    except:
        db.rollback()

    return db_movimentacao

def update_movimentacao(db: Session, movimentacao_id: int,  movimentacao: schemas.MovimentacaoCreate):
    db_movimentacao_atualizado = models.Movimentacao(**movimentacao.dict())
    db_movimentacao_antigo = db.query(models.Movimentacao).filter(models.Movimentacao.id_mov == movimentacao_id).first()
    db_product_antigo = db.query(models.Estoque).filter(models.Estoque.id == db_movimentacao_antigo.product_id).first()
    db_product_atualizado = db.query(models.Estoque).filter(models.Estoque.id == db_movimentacao_atualizado.product_id).first()
    try:
        if db_product_antigo.id != db_product_atualizado.id:
            db_product_antigo.qtd -= db_movimentacao_antigo.qtd
            db_product_atualizado.qtd += db_movimentacao_atualizado.qtd
        else:
            db_product_antigo.qtd -= db_movimentacao_antigo.qtd
            db_product_antigo.qtd += db_movimentacao_atualizado.qtd
        db_movimentacao_antigo.id = movimentacao_id
        db_movimentacao_antigo.product_id = db_movimentacao_atualizado.product_id
        db_movimentacao_antigo.qtd = db_movimentacao_atualizado.qtd
        db.commit()
    except:
        db.rollback()

    return db_movimentacao_antigo
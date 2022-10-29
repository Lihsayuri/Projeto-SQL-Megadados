from itertools import product
from sqlalchemy.orm import Session

import models, schemas


def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session):
    return db.query(models.Product).all()

# faça função para criar produto no banco de dados no mysql
def create_product(db: Session, product: schemas.ProductCreate, user_id: int):
    # cria produto no banco de dados e retorna o produto criado
    db_product = models.Product(**product.dict(), user_id=user_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product: schemas.ProductCreate, product_id: int):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    db_product.name = product.name
    db_product.qtd = product.qtd
    db.commit()
    db.refresh(db_product)
    return db_product

# função para deletar produto no banco de dados no mysql
def delete_product(db: Session, product_id: int):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    db.delete(db_product)
    db.commit()
    return db_product


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session):
    return db.query(models.User).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, first_name=user.first_name, last_name=user.last_name, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(db_user)
    db.commit()
    return db_user


# def create_product(db: Session, product: schemas.ProductCreate):
#     # cria produto no banco de dados e retorna o produto criado
#     db_product = models.Product(**product.dict())
#     db.add(db_product)
#     db.commit()
#     db.refresh(db_product)
#     return db_product

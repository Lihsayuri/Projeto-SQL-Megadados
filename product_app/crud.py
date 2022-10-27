from sqlalchemy.orm import Session

import models, schemas


def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session):
    return db.query(models.Product).all()


# faça função para criar produto no banco de dados no mysql
def create_product(db: Session, product: schemas.ProductBase):
    # cria produto no banco de dados e retorna o produto criado
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# função para atualizar produto no banco de dados no mysql
# def update_product(db: Session, product: schemas.ProductBase, product_id: int):
#     db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
#     db_product.name = product.name
#     db_product.qtd = product.qtd
#     db.commit()
#     db.refresh(db_product)
#     return db_product

# função para deletar produto no banco de dados no mysql
# def delete_product(db: Session, product_id: int):
#     db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
#     db.delete(db_product)
#     db.commit()
#     return db_product
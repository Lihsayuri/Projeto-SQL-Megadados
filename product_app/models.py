from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


# Crie classe baseada no product.py
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), index=True)
    qtd = Column(Integer, index=True)

    user = relationship("User", back_populates="products")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email =  Column(String(120), index=True, unique = True)
    first_name =   Column(String(80))
    last_name =  Column(String(80))
    hashed_password = Column(String)
    
    products = relationship("Product", back_populates="user")



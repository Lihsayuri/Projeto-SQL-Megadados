from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref

from database import Base


class Movimentacao(Base):
    __tablename__ = "movimentacao"

    id_mov = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("estoque.id"))
    qtd = Column(Integer)

    estoque = relationship("Estoque", back_populates="movimentacao")
    # estoque = relationship("Estoque", backref = backref("movimentacao", cascade = "all, delete")) 


class Estoque(Base):
    __tablename__ = "estoque"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(300), index=True)
    qtd = Column(Integer, primary_key = True, index=True, default=0)
    available = Column(Boolean, default=True)

    movimentacao = relationship("Movimentacao", back_populates="estoque", cascade="all, delete")
    # movimentacao = relationship("Movimentacao", backref = backref("estoque", cascade = "all, delete")) 








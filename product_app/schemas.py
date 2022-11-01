from unicodedata import name
from pydantic import BaseModel,Field

class EstoqueBase(BaseModel):
    id: int = Field(default=None, title="ID do produto")
    name: str = Field(default = "Placeholder", title="O nome do produto", max_length=300, example="Maçã")


class EstoqueCreate(EstoqueBase):
    pass

class Estoque(EstoqueBase):
    id : int = Field(default=None, title="ID do produto")
    qtd : int = Field(default = 0,  title = "A quantidade do produto", description="A quantidade pode ser negativa (caso você esteja diminuindo do estoque)", example=4)

    class Config:
        orm_mode = True

class MovimentacaoBase(BaseModel):
    id_mov: int = Field(default=None, title="ID da movimentação")
    qtd: int = Field(title="A quantidade do produto", description="A quantidade pode ser negativa (caso você esteja diminuindo do estoque)", example=4)


class MovimentacaoCreate(MovimentacaoBase):
    product_id: int = Field(default=None, title="ID do produto")

    pass

class Movimentacao(MovimentacaoBase):
    product_id: int = Field(default=None, title="ID do produto")

    class Config:
        orm_mode = True
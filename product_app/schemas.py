from unicodedata import name
from pydantic import BaseModel,Field

class EstoqueBase(BaseModel):
    id: int = Field(default=None, title="ID do produto")
    name: str = Field(default = "Placeholder", title="O nome do produto", max_length=300, example="Maçã")


class EstoqueCreate(EstoqueBase):
    pass

class EstoqueUpdate(EstoqueBase):
    available: bool = Field(default = True, title = "Se o produto está disponível", description="Se o produto está disponível no estoque", example=True)

class Estoque(EstoqueBase):
    qtd : int = Field(default = 0,  title = "A quantidade do produto", description="A quantidade pode ser negativa (caso você esteja diminuindo do estoque)", example=4)
    available: bool = Field(default = True, title = "Se o produto está disponível", description="Se o produto está disponível no estoque", example=True)

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
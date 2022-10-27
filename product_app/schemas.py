from pydantic import BaseModel,Field

class ProductBase(BaseModel):
    name: str = Field(default = "Placeholder", title="O nome do produto", max_length=300, example="Maçã")
    qtd : int = Field(default = 0,  title = "A quantidade do produto", ge=0, description="A quantidade não pode ser negativa", example=4)
    class Config:
        orm_mode = True
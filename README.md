# Projeto-SQL-Megadados <img src="https://img.shields.io/static/v1?label=Fase2&message=Finalizado&color=success&style=flat-square&logo=ghost"/>

## Integrantes :raising_hand_man: :raising_hand_woman: : 

- Bernardo Cunha Capoferri;
- Lívia Sayuri Makuta.

## Linguagem utilizada :desktop_computer::

- <img src="https://img.shields.io/static/v1?label=Code&message=Python&color=important&style=plastic&labelColor=black&logo=python"/>

## Framework utilizado :hammer_and_wrench: : 
- <img src="https://img.shields.io/static/v1?label=Code&message=FastAPI&color=important&style=plastic&labelColor=black&logo=FastAPI"/>

## :pushpin: O que foi feito na fase 2 :

- CRUD implementada.
- Para o banco de dados foi utilizado o banco de dados mysql.
    - No banco de dados temos duas tabelas: a de Estoque e a de Movimentação.
    - Cada produto do estoque tem: um id, nome, uma quantidade.
    - Cada movimentação na tabela de movimentação tem: um id, o id do produto sendo alterado, e a quantidade.
- Observação: ao criar o produto no estoque a quantidade será 0 por default e apenas será alterada com as movimentações daquele produto. Do mesmo modo, ao tentar editar o produto diretamente na tabela de Estoque, o usuário apenas poderá alterar o nome. E ao deletar o produto do Estoque, ele também deleta as movimentações relacionadas a esse produto.  


## Modo de uso:

- Primeiro: entre na pasta product_app:
- Depois é preciso rodar:

`uvicorn product:app --reload`

- E por fim, para fazer o teste de cada função, acesse:

`http://127.0.0.1:8000/docs`

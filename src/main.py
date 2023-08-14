import os
from typing import List

import sqlalchemy.exc
from fastapi import FastAPI, HTTPException, Query, Response, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
from models import Base, Pessoa as PessoaDB, Stack as StackDB, pessoa_stack_table
from pydantic import BaseModel

app = FastAPI()

DATABASE_URL = os.environ.get('DATABASE_URL', "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


class Stack(BaseModel):
    nome: str


class Pessoa(BaseModel):
    apelido: str
    nome: str
    nascimento: str
    stack: Optional[List[str]] = []


@app.post("/pessoas", response_model=Pessoa)
def criar_pessoa(pessoa: Pessoa):
    with SessionLocal() as db:
        pessoa.stack = [] if pessoa.stack is None else pessoa.stack
        associate_stacks = StackDB.get_or_create(session=db, stacks=[StackDB(nome=nome) for nome in pessoa.stack])
        db_pessoa = PessoaDB(**pessoa.model_dump(exclude={'stack'}))
        try:
            db.add(db_pessoa)
            db.commit()
        except sqlalchemy.exc.IntegrityError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Apelido já cadastrado!")

        db.refresh(db_pessoa)
        for stack in associate_stacks:
            associate = pessoa_stack_table.insert().values(
                pessoa_id=db_pessoa.id,
                stack_id=stack.id
            )
            db.execute(associate)

        db.commit()
    return pessoa.model_dump()


@app.get("/pessoas/{pessoa_id}", response_model=Pessoa)
def consultar_pessoa(pessoa_id: str):
    with SessionLocal() as db:
        pessoa = db.query(PessoaDB).filter(PessoaDB.id == pessoa_id).first()
        if pessoa:
            pessoa_dict = pessoa.get_dict(session=db)
            return pessoa_dict
    raise HTTPException(status_code=404, detail="Pessoa não encontrada")


@app.get("/pessoas", response_model=list[Pessoa])
def buscar_pessoas(t: Optional[str] = Query(None, title="Termo de busca")):
    with SessionLocal() as db:
        pessoas = []
        if t:
            pessoas = [p.get_dict(session=db) for p in PessoaDB.consulta_pessoa_por_termo(db, t)]
        return pessoas


@app.get("/contagem-pessoas")
def contagem_pessoas():
    return {"contagem": 1}
    # with SessionLocal() as db:
    #     count = db.query(PessoaDB).count()
    #     return {"contagem": count}

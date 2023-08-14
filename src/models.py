from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Session
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import or_


class Base(DeclarativeBase):
    pass


class Stack(Base):
    __tablename__ = "stacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement="auto")
    nome: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)

    @staticmethod
    def consulta_stack_por_nome(session: Session, nome: str):
        return session.query(Stack).filter(Stack.nome.ilike(f"{nome}")).first()

    @staticmethod
    def get_or_create(session: Session, stacks: list):
        associate_stacks = []
        for stack in stacks:
            stack_exists = Stack.consulta_stack_por_nome(session=session, nome=stack.nome)
            if stack_exists:
                associate_stacks.append(stack_exists)
            else:
                session.add(stack)
                session.commit()
                session.refresh(stack)
                associate_stacks.append(stack)
        return associate_stacks


class Pessoa(Base):
    __tablename__ = "pessoas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement="auto")
    apelido: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    nascimento: Mapped[str] = mapped_column(String(10), nullable=False)

    @staticmethod
    def consultar_stacks_de_pessoa(session: Session, _id: int):
        stacks = [p.stack_id for p in session.query(pessoa_stack_table).filter(pessoa_stack_table.c.pessoa_id == _id)]
        return [s.nome for s in session.query(Stack).filter(Stack.id.in_(stacks))]

    @staticmethod
    def consulta_pessoa_por_termo(session: Session, termo: str):
        pessoas = session.query(Pessoa)\
            .join(pessoa_stack_table, pessoa_stack_table.c.pessoa_id == Pessoa.id, isouter=True)\
            .join(Stack, pessoa_stack_table.c.stack_id == Stack.id, isouter=True)\
            .filter(
            or_(
                Pessoa.apelido.ilike(f"%{termo}%"),
                Pessoa.nome.ilike(f"%{termo}%"),
                Stack.nome.ilike(f"%{termo}%")
            )).limit(50).all()
        return pessoas

    def get_dict(self, session: Session):
        return {
            'id': self.id,
            'apelido': self.apelido,
            'nome': self.nome,
            'nascimento': self.nascimento,
            'stack': self.consultar_stacks_de_pessoa(session, self.id)
        }


pessoa_stack_table = Table(
    "pessoa_stack_table",
    Base.metadata,
    Column("pessoa_id", ForeignKey("pessoas.id"), index=True),
    Column("stack_id", ForeignKey("stacks.id"), index=True)
)

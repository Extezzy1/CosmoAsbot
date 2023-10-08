import datetime

from sqlalchemy.orm import relationship, mapped_column

from .base import BaseModel
from sqlalchemy import Column, Integer, VARCHAR, Date, Boolean, ForeignKey, DateTime, Text, BigInteger


class User(BaseModel):

    __tablename__ = "users"

    user_id = Column(BigInteger, nullable=False, unique=True, primary_key=True)
    username = Column(VARCHAR(255), nullable=True, unique=False)
    fio = Column(VARCHAR(255), nullable=True, unique=False)
    phone = Column(VARCHAR(20), nullable=True, unique=False)
    email = Column(VARCHAR(255), nullable=True, unique=False)

    is_subscribe = Column(Boolean, nullable=True, default=False, unique=False)

    def __str__(self) -> str:
        return f"User:{self.user_id}"


class Subscribe(BaseModel):

    __tablename__ = "subscribes"

    subscribe_id = Column(Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    user_id = mapped_column(ForeignKey("users.user_id"))
    is_active = Column(Boolean, nullable=False, default=True)
    date_start = Column(DateTime, default=datetime.datetime.now(), nullable=False)
    date_end = Column(DateTime, nullable=False)


class Payments(BaseModel):

    __tablename__ = "payments"

    payment_id = Column(Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    user_id = mapped_column(ForeignKey("users.user_id"))
    value = Column(Integer, nullable=False)



class Procedures(BaseModel):

    __tablename__ = "procedures"

    procedure_id = Column(Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    procedure_name = Column(Text, nullable=False)


class SubProcedures(BaseModel):

    __tablename__ = "sub_procedures"
    sub_procedure_id = Column(Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    procedure_id = mapped_column(ForeignKey("procedures.procedure_id"))
    procedure_subname = Column(Text, nullable=False)
    procedure_code = Column(VARCHAR(255), nullable=False)
    procedure_description = Column(Text, nullable=True)


class Atlas(BaseModel):

    __tablename__ = "atlas"

    atlas_entry_id = Column(Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    atlas_entry_text = Column(VARCHAR(255), nullable=False)


class AtlasPhotos(BaseModel):

    __tablename__ = "atlas_photos"

    altas_entry_id = mapped_column(ForeignKey("atlas.atlas_entry_id"))
    atlas_photo_id = Column(Text, nullable=False, primary_key=True, unique=True)


class MemoProcedure(BaseModel):

    __tablename__ = "memo_procedure"
    procedure_id = Column(Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    procedure_title = Column(Text, nullable=False, primary_key=True, unique=True)


class Memo(BaseModel):

    __tablename__ = "memo"

    memo_id = Column(Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    procedure_id = mapped_column(ForeignKey("memo_procedure.procedure_id"))
    memo_title = Column(Text, nullable=False)
    memo_text = Column(Text, nullable=False)



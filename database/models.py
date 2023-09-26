import datetime

from sqlalchemy.orm import relationship, mapped_column

from .base import BaseModel
from sqlalchemy import Column, Integer, VARCHAR, Date, Boolean, ForeignKey


class User(BaseModel):

    __tablename__ = "users"

    user_id = Column(Integer, nullable=False, unique=True, primary_key=True)
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
    date_start = Column(Date, default=datetime.datetime.now(), nullable=False)
    date_end = Column(Date, nullable=False)


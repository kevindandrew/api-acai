# models/base.py
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy import func  # En el archivo donde defines los modelos


class Base(DeclarativeBase):
    pass

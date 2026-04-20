from sqlalchemy import Column, Integer, BigInteger, String
from data.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(128), nullable=True)
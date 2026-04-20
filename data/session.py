from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# SQLite — один файл базы данных (очень удобно)
DATABASE_URL = "sqlite:///raspisalka.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},   # обязательно для aiogram
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./pc_components_100.db"

engine1 = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
Base1 = declarative_base()


def get_db1():
    db = SessionLocal1()
    try:
        yield db
    finally:
        db.close()

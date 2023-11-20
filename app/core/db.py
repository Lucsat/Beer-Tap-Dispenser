import os

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "")


# Dependencia (DI)
def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(metadata=MetaData())

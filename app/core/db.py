from sqlmodel import Session, create_engine
from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)  # echo=True para depuración

def get_db():
    with Session(engine) as session:
        yield session
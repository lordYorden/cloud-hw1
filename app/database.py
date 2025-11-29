from sqlmodel import create_engine, SQLModel, Session
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

DATABASE_URL = os.getenv('DB_PATH')
if not DATABASE_URL:
    raise ValueError("DB_PATH not found in .env file")

engine = create_engine(DATABASE_URL, echo=True)
    
def get_session():
    with Session(engine) as session:
        yield session

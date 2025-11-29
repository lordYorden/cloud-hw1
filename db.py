from sqlmodel import create_engine, SQLModel, Session
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

DATABASE_URL = os.getenv('DB_PATH') or 'sqlite:///./test.db' # Default to sqlite if not found
engine = create_engine(DATABASE_URL, echo=True)
    
def get_session():
    with Session(engine) as session:
        yield session
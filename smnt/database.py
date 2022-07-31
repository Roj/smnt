from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from smnt.config import DB_STRING

from smnt.models import Base

engine = create_engine(DB_STRING, future=True)
Base.metadata.create_all(engine)

Session = sessionmaker(engine)

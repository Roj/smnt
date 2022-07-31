from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smnt.models import Base

engine = create_engine("sqlite+pysqlite:///db.db", echo=True, future=True)
Base.metadata.create_all(engine)

Session = sessionmaker(engine)

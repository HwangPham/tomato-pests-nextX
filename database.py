from sqlalchemy import Column, ForeignKey, Integer, Float, String
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    # Here we define columns for the table user.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

class Result(Base):
    __tablename__ = 'result'
    # Here we define columns for the table result.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True, nullable=False)
    plant_id= Column(Integer, nullable=False)
    url = Column(String(250), nullable=False)
    pest = Column(String(250))
    percentage = Column(Float)
    user_id = Column(Integer, ForeignKey('user.id'))
    person = relationship(User)

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///./sqlalchemy_tomato.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(bind=engine)

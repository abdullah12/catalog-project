from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    items = relationship("CategoryItem", cascade="all, delete-orphan")



class CategoryItem(Base):
    __tablename__ = 'items'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'))

engine = create_engine('sqlite:///catalog3.db')
Base.metadata.create_all(engine)

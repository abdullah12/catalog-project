from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db2 import Category, CategoryItem, Base

engine = create_engine('sqlite:///catalog3.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Clear database
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)




category1 = Category(name="animal")
session.add(category1)
session.commit()

category2 = Category(name="bird")
session.add(category2)
session.commit()

category3 = Category(name="plant")
session.add(category3)
session.commit()

item1 = CategoryItem(name="lion",category_id="1")
session.add(item1)
session.commit()

item2 = CategoryItem(name="goat",category_id="1")
session.add(item2)
session.commit()

s1 = session.query(Category).filter_by(id=1).one()

session.delete(s1)
session.commit()
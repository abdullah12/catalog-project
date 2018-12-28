from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User,Category,CategoryItem, Base

engine = create_engine('sqlite:///catalog.db')
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


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


category1 = Category(name="animal",user_id="1")
session.add(category1)
session.commit()

category2 = Category(name="bird",user_id="1")
session.add(category2)
session.commit()

category3 = Category(name="plant",user_id="1")
session.add(category3)
session.commit()

item1 = CategoryItem(name="lion",description="it is a lion",user_id="1",category_id="1")
session.add(item1)
session.commit()

item2 = CategoryItem(name="goat",description="it is a goat",user_id="1",category_id="1")
session.add(item2)
session.commit()

item3 = CategoryItem(name="fox",description="it is a fox",user_id="1",category_id="1")
session.add(item3)
session.commit()


item4 = CategoryItem(name="eagle",description="it is a eagle",user_id="1",category_id="2")
session.add(item4)
session.commit()

item5 = CategoryItem(name="parrot",description="it is a parrot",user_id="1",category_id="2")
session.add(item5)
session.commit()

item6 = CategoryItem(name="duck",description="it is a duck",user_id="1",category_id="2")
session.add(item6)
session.commit()

item7 = CategoryItem(name="orange",description="it is a orange",user_id="1",category_id="3")
session.add(item7)
session.commit()

item8 = CategoryItem(name="apple",description="it is a apple",user_id="1",category_id="3")
session.add(item8)
session.commit()

item9 = CategoryItem(name="dates",description="it is a dates",user_id="1",category_id="3")
session.add(item9)
session.commit()
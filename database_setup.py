# configuration header
import sys, datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base = declarative_base()

# item definition
class Item(Base):
	__tablename__ = 'item'
	# mapping
	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	description = Column(String(250))
	category_name = Column(String(80), ForeignKey('category.name'))
	date_added = Column(DateTime, default = datetime.datetime.utcnow)

class Category(Base):
	__tablename__ = 'category'
	name = Column(String(80), primary_key = True, nullable = False)

# configuration footer
engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)

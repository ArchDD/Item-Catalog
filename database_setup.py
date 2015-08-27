# configuration header
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


# item definition
class Item(Base):
    __tablename__ = 'item'
    # mapping
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    category_name = Column(String(80), ForeignKey('category.name'))
    date_added = Column(DateTime, default=datetime.datetime.utcnow)

    # Serialize function to send JSON objects
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_name': self.category_name,
            'date_added': self.date_added,
        }


class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), primary_key=True, nullable=False)

    @property
    def serialize(self):

        return {
            'name': self.name
        }

# configuration footer
engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)

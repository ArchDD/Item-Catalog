# Item Catalog
A basic item catalog website that lets you add items once logged in through a Google+ account

## Table of contents

- [What's included](#What's included)
- [Creators](#creators)
- [Copyright and license](#copyright-and-license)

### What's included

```
catalog/
├── application.py
├── database_setup.py
├── client_secrets.json
├── catalog.db
├── templates/
  ├── category.html/
  ├── createitem.html/
  ├── deleteitem.html/
  ├── home.html/
  ├── item.html/
  ├── login.html/
  └── updateitem.html/
└── static/
  └── style.css
```

## Software Requirements

Python 2.7.10

Werkzeug 0.8.3

Flask 0.9

Flask-Login 0.1.3

## Setup Instructions

### Database creation

1. Navigate to the catalog directory in command line or terminal
2. Run database_setup.py with command 'python database_setup.py'

### Database poulating
1. Navigate to the catalog directory in command line or terminal
2. Start python with command 'python'
3. Create a session for the database via python, for example
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker
  from database_setup import Base, Category, Item
  engine = create_eingine('sqlite:///catalog.db')
  Base.metadata.bind = engine
  DBSession = sessionmaker(bind = engine)
  session = DBSession()
4. Create and add a new object then commit, for example
  newCategory = Category(name = "uncategorised")
  session.add(newCategory)
  session.commit()

Alternatively a python file can be used instead.

### Running website

1. Navigate to the catalog directory in command line or terminal
2. Run the application python script with command 'python application.py'
3. Visit 'http://localhost:8000/' on a browser

application.py can be configured to use another port or a server, google api must be updated accordingly.


## Creators

**Dillon Keith Diep**


## Copyright and license

The code released was created for educational purposes, copyright and license subject to Udacity's provided source code - no other enforcements otherwise.

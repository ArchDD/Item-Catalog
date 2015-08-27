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

### Database populating
1. Navigate to the catalog directory in command line or terminal
2. Start python with command 'python'
3. Create a session for the database via python, for example
  
  from sqlalchemy import create_engine

  from sqlalchemy.orm import sessionmaker
  
  from database_setup import Base, Category, Item
  
  engine = create_engine('sqlite:///catalog.db')
  
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

### Using website

1. At home the 10 latest items are displayed, along with all catogories listed. You may reach the login page through the login button
2. At the login page you may use Google Plus to login
3. Clicking on a category goes to the category page that lists all items under that category. Here you may add new items if you are logged on, otherwise the button will redirect you to the login page.
4. Clicking on a item goes to the item page which can be edited or deleted by users logged in, otherwise it redirects you to the login page.

## Creators

**Dillon Keith Diep**


## Copyright and license

The code released was created for educational purposes, copyright and license subject to Udacity's provided source code - no other enforcements otherwise.

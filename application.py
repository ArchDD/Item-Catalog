from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'super secret key'

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# adding database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#need template page to show categories at side every page
#need json endpoint

@app.route('/')
def homepage():
    return "Need html for latest items"

@app.route('/categories/<string:category_name>/')
def categoryList(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_name=category_name)
    return render_template('category.html', category=category, items=items, category_name=category_name)

@app.route('/categories/')
def categories(category_name):
    categories = session.query(Category).all()
    output = ''
    for category in categories:
        output += category.name
        output += '</br>' 
    return output

@app.route('/items/<string:category_name>/create/', methods = ['GET', 'POST'])
def createItem(category_name):
    if request.method == 'POST':
        createdItem = Item(name = request.form['name'],
                           description = request.form['description'],
                           category_name = category_name)
        session.add(createdItem)
        session.commit
        return redirect(url_for('categoryList', category_name=category_name))
    else:
        return render_template('createitem.html', category_name=category_name)


@app.route('/categories/<string:category_name>/<int:item_id>/update',
           methods=['GET', 'POST'])
def updateItem(category_name, item_id):
    updatedItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            updatedItem.name = request.form['name']
        if request.form['description']:
            updatedItem.description = request.form['description']
        session.add(updatedItem)
        session.commit()
        return redirect(url_for('categoryList', category_name=category_name))
    else:

        return render_template(
            'updateitem.html', category_name=category_name, item_id=item_id, item=updatedItem)

@app.route('/categories/<string:category_name>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_id):
    deletingItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(deletingItem)
        session.commit()
        return redirect(url_for('categoryList', category_name=category_name))
    else:
        return render_template('deleteitem.html', item=deletingItem)

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    print 'start gconnect'
    # Only if collect one-time code if state token matches
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    print 'wtf'
    # Exchange one-time code for credentials object
    try:
        print 'trying'
        oauth_flow=flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        print 'ye'
        credentials = oauth_flow.step2_exchange(code)
        print 'no'
    except FlowExchangeError:
        print 'butt failed'
        response = make_response(json.dumps('Failed to upgrade the authorisation code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'aouch'
    # Check for valid access token
    access_token = login_session.get('credentials')
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    print 'halp'
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application.json'
    # Confirm credential id match
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Confirm client id match
    if result['issued-to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check for user already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        print "stuch here"
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
    print 'yay'
    # Store credentials for future use
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Retrieve information from Google API
    userinfo_url = "https://www.googleapis.com/oauth2/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #Display log in
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += 'img src="'
    output += login_session['picture']
    output += ' " style = "width:300px; height: 300px; border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius:150px;">'
    flash("You are now logged in as %s"%login_session['username'])
    print output
    return output

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
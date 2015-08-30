import random
import string
import httplib2
import json
import requests
from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify, flash, make_response, session as login_session
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'super secret key'

file_name = 'client_secrets.json'
CLIENT_ID = json.loads(open(file_name, 'r').read())['web']['client_id']

# adding database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# JSON API endpoints
@app.route('/categories/<string:category_name>/JSON')
def categoryListJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_name=category_name)
    return jsonify(CategoryItems=[i.serialize for i in items])


@app.route('/categories/<int:item_id>/JSON')
def itemJSON(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


# hompage shows latest items
@app.route('/')
def homepage():
    # all categories to be listed
    categories = session.query(Category).all()
    # get latest items ordered by date and limit to 10
    all_latest_items = session.query(Item).order_by(desc(Item.date_added))
    latest_items = all_latest_items.limit(10).all()
    return render_template('home.html', categories=categories,
                           latest_items=latest_items)


# a specific category page
@app.route('/categories/<string:category_name>/')
def categoryList(category_name):
    # all categories still displayed on side bar
    categories = session.query(Category).all()
    # retrieve matching category by name
    category = session.query(Category).filter_by(name=category_name).one()
    # retrieve all items of matching category
    items = session.query(Item).filter_by(category_name=category_name)
    return render_template('category.html', categories=categories,
                           category=category, items=items)


# the item page displays properties regarding that item
@app.route('/categories/<string:category_name>/<int:item_id>/')
def item(category_name, item_id):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('item.html', category=category, item=item)


@app.route('/items/<string:category_name>/create/', methods=['GET', 'POST'])
def createItem(category_name):
    # directs user to login page if not logged on
    if 'username' not in login_session:
        return redirect('/login')
    # GET method shows form, POST creates item on database
    if request.method == 'POST':
        # create a new item object to be added on database
        createdItem = Item(name=request.form['name'],
                           description=request.form['description'],
                           category_name=category_name)
        session.add(createdItem)
        # commit to save changes
        session.commit()
        return redirect(url_for('categoryList', category_name=category_name))
    else:
        return render_template('createitem.html', category_name=category_name)


@app.route('/categories/<string:category_name>/<int:item_id>/update',
           methods=['GET', 'POST'])
def updateItem(category_name, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    updatedItem = session.query(Item).filter_by(id=item_id).one()
    # GET method shows form, POST updates item on database
    if request.method == 'POST':
        # update item properties
        if request.form['name']:
            updatedItem.name = request.form['name']
        if request.form['description']:
            updatedItem.description = request.form['description']
        session.add(updatedItem)
        session.commit()
        return redirect(url_for('categoryList', category_name=category_name))
    else:
        return render_template('updateitem.html', category_name=category_name,
                               item_id=item_id, item=updatedItem)


@app.route('/categories/<string:category_name>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletingItem = session.query(Item).filter_by(id=item_id).one()
    # GET method shows page to confirm deletion, POST deletes item on database
    if request.method == 'POST':
        session.delete(deletingItem)
        session.commit()
        return redirect(url_for('categoryList', category_name=category_name))
    else:
        return render_template('deleteitem.html', item=deletingItem)


@app.route('/login')
def showLogin():
    # generate state for confirmation
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/logout')
def showLogout():
    state = login_session['state']
    return render_template('logout.html', STATE=state)


# connecting to google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # only collect one-time code if state token matches
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    # exchange one-time code for credentials object
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response_message = 'Failed to upgrade the authorisation code.'
        response = make_response(json.dumps(response_message), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # check for valid access token
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # confirm credential id match
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # confirm client id match
    if result['issued_to'] != CLIENT_ID:
        response_message = "Token's client ID does not match app's."
        response = make_response(json.dumps(response_message), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # check for user already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response_message = 'Current user is already connected.'
        response = make_response(json.dumps(response_message), 200)
        response.headers['Content-Type'] = 'application/json'
    # store credentials for future use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # retrieve information from Google API
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # indicate logging on
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


# disconnect from google
@app.route("/gdisconnect")
def gdisconnect():
    # only disconnect a connected user
    credentials = login_session.get('access_token')
    if credentials is None:
        response = make_response(json.dumps('No user connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # upon success reset session
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('User disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('You were successfully logged out!')
        return redirect(url_for('homepage'),302)
    else:
        response_message = 'Failed to revoke token for given user.'
        response = make_response(json.dumps(response_message), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

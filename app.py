from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response, flash
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                   json.dumps('Current user is already connected.'),
                   200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px;
              height: 300px;border-radius: 150px;
              -webkit-border-radius: 150px;
              -moz-border-radius: 150px;">
              '''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except SQLAlchemyError as ex:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response
        (json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Category Information
@app.route('/category/<int:category_id>/menu/JSON')
def categoryMenuJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem).filter_by(
        category_id=category_id).all()
    return jsonify(CategoryItems=[i.serialize for i in items])


@app.route('/category/<int:category_id>/menu/<int:item_id>/JSON')
def menuItemJSON(category_id, item_id):
    Category_Item = session.query(CategoryItem).filter_by(id=item_id).one()
    return jsonify(Category_Item=Category_Item.serialize)


@app.route('/category/JSON')
def restaurantsJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Show all restaurants
@app.route('/')
def showCategories():
    categories = session.query(Category).all()

    categoryItems = session.query(CategoryItem).all()

    return render_template('categories.html',
                           categories=categories,
                           categoryItems=categoryItems)


# Show a category Items
@app.route('/category/<int:category_id>')
@app.route('/category/<int:category_id>/items')
def showCategory(category_id):
    # Get all categories
    categories = session.query(Category).all()

    # Get category
    category = session.query(Category).filter_by(id=category_id).first()

    # Get name of category
    categoryName = category.name

    # Get all items of a specific category
    categoryItems = session.query(CategoryItem) \
        .filter_by(category_id=category_id).all()

    # Get count of category items
    categoryItemsCount = \
        session.query(CategoryItem).filter_by(category_id=category_id).count()

    return render_template('category.html', categories=categories,
                           categoryItems=categoryItems,
                           categoryName=categoryName,
                           categoryItemsCount=categoryItemsCount)


# Show a category Item
@app.route('/category/<int:category_id>/items/<int:item_id>')
def showCategoryItem(category_id, item_id):
    # Get category item
    categoryItem = session.query(CategoryItem).filter_by(id=item_id).first()

    # Get creator of item
    creator = getUserInfo(categoryItem.user_id)

    return render_template('categoryItem.html',
                           categoryItem=categoryItem, creator=creator)


# Edit a category item
@app.route('/catalog/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editCategoryItem(category_id, item_id):
    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')

    # Get category item
    categoryItem = session.query(CategoryItem).filter_by(id=item_id).first()

    # Get creator of item
    creator = getUserInfo(categoryItem.user_id)

    # Check if logged in user is creator of category item
    if creator.id != login_session['user_id']:
        return redirect('/login')

    # Get all categories
    categories = session.query(Category).all()

    if request.method == 'POST':
        if request.form['name']:
            categoryItem.name = request.form['name']
        if request.form['description']:
            categoryItem.description = request.form['description']
        if request.form['category']:
            categoryItem.category_id = request.form['category']
        return redirect(url_for('showCategoryItem',
                                category_id=categoryItem.category_id,
                                item_id=categoryItem.id))
    else:
        return render_template('editCategoryItem.html',
                               categories=categories,
                               categoryItem=categoryItem)


# Delete a Category item

@app.route('/catalog/<int:category_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteCategoryItem(category_id, item_id):
    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')

    # Get category item
    categoryItem = session.query(CategoryItem).filter_by(id=item_id).first()

    # Get creator of item
    creator = getUserInfo(categoryItem.user_id)

    # Check if logged in user is creator of category item
    if creator.id != login_session['user_id']:
        return redirect('/login')

    if request.method == 'POST':
        session.delete(categoryItem)
        session.commit()
        return redirect(url_for('showCategory',
                                category_id=categoryItem.category_id))
    else:
        return render_template('deleteCategoryItem.html',
                               categoryItem=categoryItem)


@app.route('/category/add', methods=['GET', 'POST'])
def addCategoryItem():
    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        # TODO: Retain data when there is an error

        if not request.form['name']:
            flash('Please add instrument name')
            return redirect(url_for('addCategoryItem'))

        if not request.form['description']:
            flash('Please add a description')
            return redirect(url_for('addCategoryItem'))

        # Add category item
        newCategoryItem = CategoryItem(name=request.form['name'],
                                       description=request.form['description'],
                                       category_id=request.form['category'],
                                       user_id=login_session['user_id'])
        session.add(newCategoryItem)
        session.commit()

        return redirect(url_for('showCategories'))
    else:
        # Get all categories
        categories = session.query(Category).all()

        return render_template('addCategoryItem.html', categories=categories)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

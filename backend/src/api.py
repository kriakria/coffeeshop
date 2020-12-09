import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES


@app.route('/coffee')
def landing_page():
    return 'coffee :)'


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():

    # drinks = Drink.query.all()
    short_drinks = get_short_drinks()

    data = []

    try:
        if short_drinks:
            print("drinks")
            # data = [drink.short() for drink in drinks]
            for drink in short_drinks:
                data.append(drink)

        else:
            data = []

        return jsonify({
            'success': True,
            'drinks': data
        })
    except Exception as e:
        print(e)
        abort(404)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drink-test')
@requires_auth('get:drinks-detail')
def test(jwt):
    # auth_header = request.headers['Authorization']
    # header_parts = auth_header.split(' ')[1]
    # print(header_parts)
    # print(auth_header)

    return 'not implemented'


def get_short_drinks():
    drinks = Drink.query.all()
    short_drinks = []
    for drink in drinks:
        short_drinks.append(drink.short())
    return short_drinks


def get_long_drinks():
    drinks = Drink.query.all()
    long_drinks = []
    for drink in drinks:
        long_drinks.append(drink.long())
    return long_drinks


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):

    long_drinks = get_long_drinks()

    if len(long_drinks) == 0:
        abort(401)

    try:
        return jsonify({
            'success': True,
            'drinks': long_drinks

        })

    except Exception as e:
        print(e)
        abort(404)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):

    drink = request.get_json()
    new_title = drink.get('title', None)
    new_recipe = drink.get('recipe', None)

    if new_title is None:
        abort(404)

    if new_recipe is None:
        abort(404)

    new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))

    try:
        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': new_drink.long()
        })

    except Exception as e:
        print(e)
        abort(404)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

# This endpoint allows a user with 'patch:drinks' permission to edit the title of a drink
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):

    drink_update = request.get_json()
    new_title = drink_update.get('title', None)
    new_recipe = drink_update.get('recipe', None)

    try:
        if new_recipe is None:
            if new_title is None:
                print("aborted")
                abort(404)

            elif new_title is not None:
                # try:
                print("there is a new title")
                drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

                if drink is None:
                    abort(404)

                else:
                    drink.title = new_title
                    # drink.recipe = new_recipe
                    drink.insert()

                return jsonify({
                    'success': True,
                    'drinks': drink.long()
                })
    except Exception as e:
        print(e)
        abort(404)






    '''try:
        # if new_title is None:
            # abort(404)

        # else:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        else:
            drink.title = new_title
            # drink.recipe = new_recipe
            drink.insert()

            return jsonify({
                'success': True,
                'drinks': drink.long()
            })'''



'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# In this endpoint a user with 'delete:drinks' permission can delete a drink from the database
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    try:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except Exception as e:
        print(e)
        abort(404)


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(400)
def bad_request(error):

    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request'
    }), 400

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):

    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method not allowed'
    }), 405


@app.errorhandler(500)
def server_error(error):

    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal server error'
    }), 500
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def autherror(e):
    return jsonify(e.error), e.status_code

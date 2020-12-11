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
The following line should be uncommented when you initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES


'''
The get_short_drinks() methods queries all drinks in the database and
    returns all drinks in the drinks_short() data representation.
'''


def get_short_drinks():
    drinks = Drink.query.all()
    short_drinks = []
    for drink in drinks:
        short_drinks.append(drink.short())
    return short_drinks


'''
The get_long_drinks() methods queries all drinks in the database and
    returns all drinks in the drinks_long() data representation.
'''


def get_long_drinks():
    drinks = Drink.query.all()
    long_drinks = []
    for drink in drinks:
        long_drinks.append(drink.long())
    return long_drinks


'''
The GET /drinks endpoint is a public endpoint that calls the get_short_drinks()
    method to get a list of drinks in the database in the drink.short()
    data representation, and returns the list of drinks in an array,
    or the 404 status code in case of failure.
    If there are no drinks in the database, there is a 401 abort.
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():

    short_drinks = get_short_drinks()

    if len(long_drinks) == 0:
        abort(401)

    data = []

    try:
        if short_drinks:
            for drink in short_drinks:
                data.append(drink)

        else:
            data = []

        return jsonify({
            'success': True,
            'drinks': data
        }), 200

    except Exception as e:
        print(e)
        abort(404)


'''
The GET /drinks-detail endpoint requires the 'get:drinks-detail' permission.
    It calls the get_long_drinks() method to get a list of drinks in the
    database in the drink.long() data representation, and returns the list of
    drinks in an array, or the 404 status code in case of failure.
    If there are no drinks in the database, there is a 401 abort.
'''


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
        }), 200

    except Exception as e:
        print(e)
        abort(404)


'''
The POST /drinks endpoint requires the 'post:drinks' permission.
    It creates a new row in the drinks table with the drink.long()
    date representation, or the 404 status code in case of failure.
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):

    drink = request.get_json()
    new_title = drink.get('title', None)
    new_recipe = drink.get('recipe', None)

    new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))

    try:
        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': new_drink.long()
        }), 200

    except Exception as e:
        print(e)
        abort(404)


'''
The PATCH /drinks/<int:drink_id> endpoint requires the 'patch:drinks'
    permission.
    drink_id is the ID of the drink that will be edited. If the drink ID
    can not be found it responds with a 404 error.
    If the ID is found, the corresponding row for the ID is updated with
    the drink.long() data representation.
    On a successful update, the endpoint returns a 200 code and an array
    of drinks, or error 404 in case of failure.
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):

    drink_update = request.get_json()
    new_title = drink_update.get('title', None)
    new_recipe = drink_update.get('recipe', None)

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if not drink:
            abort(404)

        drink.title = new_title
        drink.recipe = json.dumps(new_recipe)
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception as e:
        print(e)
        abort(404)


'''
The DELETE /drinks/<id> endpoint requires the 'delete:drink' permission.
    drink_id is the ID of the drink that will be edited. If the drink ID
    can not be found it responds with a 404 error.
    If the ID is found then the corresponding row is deleted from the database.
    On a successful delete, the endpoint returns a 200 code and the drink that
    was deleted, or error 404 in case of failure.
'''


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
        }), 200
    except Exception as e:
        print(e)
        abort(404)


# Error Handling
'''
The error handlers use the @app.errorhandler(error) decorator.
    Each error handler returns the error coda and the approprate message.
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


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(500)
def server_error(error):

    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal server error'
    }), 500


'''
The AuthError error handler returns the error and the error code.
'''


@app.errorhandler(AuthError)
def autherror(e):
    return jsonify(e.error), e.status_code

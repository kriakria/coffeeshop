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

    drinks = Drink.query.all()  # get short()

    if drinks:
        print(drinks)
        data = [drinks.short() for drink in drinks]
    else:
        data = []

    return jsonify({
        'success': True,
        'drink': data
    })


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
def test():
    auth_header = request.headers['Authorization']
    header_parts = auth_header.split(' ')[1]
    print(header_parts)
    print(auth_header)

    return 'not implemented'


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):

    jwt = get_token_auth_header()
    print(jwt)

    drinks = Drink.query.all()  # get long()
    print(drinks)

    return jsonify({
        'success': True,
        'drinks': drinks
    })


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

    data = request.get_json()
    new_title = data.get('title', None)
    new_recipe = data.get('recipe', None)

    new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))

    try:
        # Drink.insert(new_drink)
        new_drink.insert()
        print("hello")
        return "hello"

    except Exception as e:
        print(e)
        abort(404)
    
'''    try:
        new_drink1 = Drink(
            title=new_title,
            recipe=new_recipe
        )
        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))

        # print(new_drink)
        # Drink.insert(new_drink)

        return jsonify({
            'success': True,
            'title': new_title
            # 'drinks': Drink.long(new_drink)
            # 'drinks': new_drink
        })

    except BaseException:
        abort(401)'''


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


## Error Handling
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

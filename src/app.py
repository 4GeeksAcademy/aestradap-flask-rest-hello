"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/users/<user_id>', methods = ['GET', 'POST', 'DELETE'])
def user(user_id):
    if request.method == 'GET':
         
         response_body = {
        "msg": "Hello, this is your GET /user response "
    }
         return jsonify(response_body), 200

       
    if request.method == 'POST':
        """modify/update the information for <user_id> but first you have to findthat user"""
        user_data = request.json
        new_user = User (
            email = user_data['email'],
            password = user_data['password'],
            is_active = user_data['is_active']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.serialize()), 201
     
    if request.method == 'DELETE':
        """delete user with ID <user_id>"""
        
      
    else:
       return 'Error 405 Method Not Allowed'
        
@app.route('/users', methods = ['GET', 'POST'])
def handle_users():
     if request.method == 'POST':
        user_data = request.json
        new_user = User (
            email = user_data['email'],
            password = user_data['password'],
            is_active = user_data['is_active']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.serialize()), 201
     else:
        users = User.query.all()
        dic_users = []
        for user in users:
            dic_users.append(user.serialize())
        return jsonify(dic_users), 200
        

@app.route('/planets', methods = ['GET', 'POST'])
def handle_planets():
     if request.method == 'POST':
        planet_data = request.json
        new_planet = Planet (
            name = planet_data['planet_name'],
            diameter = planet_data ['diameter']
        )
        db.session.add(new_planet)
        db.session.commit()
        return jsonify(new_planet.serialize()), 201
     else:
        planets = Planet.query.all()
        dic_planets = []
        for planet in planets:
            dic_planets.append(planet.serialize())
        return jsonify(dic_planets), 200
        
@app.route('/characters', methods = ['GET', 'POST'])
def handle_characters():
     if request.method == 'POST':
        character_data = request.json
        new_character = Character (
            name = character_data['character_name'],
        )
        db.session.add(new_character)
        db.session.commit()
        return jsonify(new_character.serialize()), 201
     else:
        characters = Character.query.all()
        dic_characters = []
        for character in characters:
            dic_characters.append(character.serialize())
        return jsonify(dic_characters), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

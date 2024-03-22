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
from models import db, User, Planet, Character, Favorite


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

# CRUD operations for user      
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
     
    # insert edit and delete     
@app.route('/users/<int:user_id>/', methods=['GET', 'POST'])
def manage_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'GET':
        # Retrieve user details and favorites
        user_data = {'id': user.id, 'username': user.username, 'email': user.email}
        user_data['favorites'] = [{'id': favorite.id,
                                   'favorite_id': favorite.favorite_id,
                                   'favorite_type': favorite.favorite_type} for favorite in user.favorites]
        return jsonify(user_data)

    elif request.method == 'POST':
        data = request.json
        favorite_type = data.get('favorite_type')
        favorite_id = data.get('favorite_id')

        if favorite_type not in ['planet', 'character']:
            return jsonify({'message': 'Invalid favorite type. Must be "planet" or "character"'}), 400

        if favorite_type == 'planet':
            item = Planet.query.get(favorite_id)
        else:
            item = Character.query.get(favorite_id)

        if item is None:
            return jsonify({'message': 'Invalid favorite item ID'}), 400

        # Check if the favorite already exists for the user
        existing_favorite = Favorite.query.filter_by(user_id=user_id, favorite_id=favorite_id, favorite_type=favorite_type).first()
        if existing_favorite:
            return jsonify({'message': 'Favorite already exists for the user'}), 409

        # Create the new favorite
        new_favorite = Favorite(user_id=user_id, favorite_id=favorite_id, favorite_type=favorite_type)
        db.session.add(new_favorite)
        db.session.commit()
        # return jsonify(new_favorite.serialize()), 201
        return jsonify({'message': 'Favorite added successfully'}), 201

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user_id = 1  # replace with actual user ID
    favorites = Favorite.query.filter_by(user_id=current_user_id).all()
    return jsonify([{'id': favorite.id,
                     'favorite_id': favorite.favorite_id, 
                      'favorite_type': favorite.favorite_type
                    } for favorite in favorites])

  #   insert edit and delete
@app.route('/favorite/planet/<int:planet_id>', methods=['POST', 'DELETE'])
def manage_planet_favorite(planet_id):
    current_user_id = 1

    if request.method == 'POST':
        # Add new favorite planet for the current user
        new_favorite = Favorite(user_id=current_user_id, favorite_id=planet_id, favorite_type='planet')
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({'message': 'Favorite planet added successfully'})

    elif request.method == 'DELETE':
        # Delete favorite planet for the current user
        favorite = Favorite.query.filter_by(user_id=current_user_id, favorite_id=planet_id, favorite_type='planet').first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({'message': 'Favorite planet deleted successfully'})
        else:
            return jsonify({'message': 'Favorite planet not found for the current user'}), 404

@app.route('/favorite/character/<int:character_id>', methods=['POST', 'DELETE'])
def manage_character_favorite(character_id):
    # For simplicity, let's assume we have a global variable current_user_id to store the current user's ID
    current_user_id = 1  # Placeholder value, replace with actual user ID

    if request.method == 'POST':
        # Add new favorite charater for the current user
        new_favorite = Favorite(user_id=current_user_id, favorite_id=character_id, favorite_type='character')
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({'message': 'Favorite charater added successfully'})

    elif request.method == 'DELETE':
        # Delete favorite charater for the current user
        favorite = Favorite.query.filter_by(user_id=current_user_id, favorite_id=character_id, favorite_type='character').first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({'message': 'Favorite character deleted successfully'})
        else:
            return jsonify({'message': 'Favorite character not found for the current user'}), 404


# CRUD operations for planets
@app.route('/planets', methods=['GET', 'POST'])
def manage_planets():
    if request.method == 'GET':
        planets = Planet.query.all()
        dic_planets = []
        for planet in planets:
            dic_planets.append(planet.serialize())
        return jsonify(dic_planets), 200
    
    elif request.method == 'POST':
        data = request.json
        new_planet = Planet(name=data['name'])
        db.session.add(new_planet)
        db.session.commit()
        return jsonify({'message': 'Planet created successfully'})
    
    #  insert edit and delete
@app.route('/planets/<int:planet_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)

    if request.method == 'GET':
        # return jsonify({'id': planet.id, 'name': planet.name})
        return jsonify(planet.serialice()), 200
        
    elif request.method == 'PUT':
        data = request.json
        new_planet = Planet (
                            name = data['name'],
                            diameter = data ['diameter']
                            )
        db.session.add(new_planet)
        db.session.commit()
        return jsonify(new_planet.serialize()), 201
    
    elif request.method == 'DELETE':
        db.session.delete(planet)
        db.session.commit()
        return jsonify({'message': 'Planet deleted successfully'})


# CRUD operations for characters
@app.route('/characters', methods=['GET', 'POST'])
def manage_characters():
    if request.method == 'GET':
         # characters = Character.query.all()
        # return jsonify([{'id': character.id, 'name': character.name} for character in characters])
        characters = Character.query.all()
        dic_charts = []
        for character in characters:
            dic_charts.append(character.serialize())
        return jsonify(dic_charts), 200
        
    elif request.method == 'POST':
        data = request.json
        new_character = Character(name = data['name'])
        db.session.add(new_character)
        db.session.commit()
        return jsonify({'message': 'Character created successfully'}), 201
    
# insert edit and delete
@app.route('/characters/<int:character_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_character(character_id):
    character = Character.query.get_or_404(character_id)
    if request.method == 'GET':
        # return jsonify({'id': character.id, 'name': character.name})
        return jsonify(character.serialize()), 200
    
    elif request.method == 'PUT':
        data = request.json
        character.name = data['name']
        db.session.commit()
        # return jsonify({'message': 'Character updated successfully'})
        return jsonify(data.serialize()) , 201
    
    elif request.method == 'DELETE':
        db.session.delete(character)
        db.session.commit()
        return jsonify({'message': 'Character deleted successfully'})





# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

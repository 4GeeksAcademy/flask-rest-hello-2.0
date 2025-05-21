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
from models import db, User, People, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False


db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)

# --- usuarios  ---


@app.route('/user', methods=['GET'])
def handle_hello():
    return jsonify({"msg": "Hello, this is your GET /user response"}), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

# --- personajes ---


@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([person.serialize() for person in people]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if not person:
        raise APIException('Person not found', status_code=404)
    return jsonify(person.serialize()), 200

# --- PLANETAS ---


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException('Planet not found', status_code=404)
    return jsonify(planet.serialize()), 200

# --- FAVORITOS ---


@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([fav.serialize() for fav in favorites]), 200


@app.route('/users/<int:user_id>/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": f"Planet with ID {planet_id} not found"}), 404

    if Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first():
        return jsonify({"error": "Planet already in favorites"}), 400

    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": f"Planet {planet.name} added to user {user_id}'s favorites"}), 201


@app.route('/users/<int:user_id>/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(user_id, people_id):

    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": f"People with ID {people_id} not found"}), 404

    if Favorite.query.filter_by(user_id=user_id, people_id=people_id).first():
        return jsonify({"error": "Person already in favorites"}), 400

    favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": f"Person {person.name} added to user {user_id}'s favorites"}), 201


@app.route('/users/<int:user_id>/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    favorite = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"error": "Favorite planet not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite planet deleted"}), 200


@app.route('/users/<int:user_id>/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(user_id, people_id):
    favorite = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()
    if not favorite:
        return jsonify({"error": "Favorite person not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite person deleted"}), 200


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

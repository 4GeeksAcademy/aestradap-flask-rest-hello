from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, declarative_base

db = SQLAlchemy()
Base = declarative_base()

class User(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    email =db.Column(db.String(120), unique=True, nullable=False)
    password =db.Column(db.String(80), unique=False, nullable=False)
    is_active =db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
            # do not serialize the password, its a security breach
        }
    
favorite_character_association = db.Table(
    'favorite_character',
    Base.metadata,
   db.Column('favorite_id', db.Integer, db.ForeignKey('favorite.id')),
   db.Column('character_id', db.Integer, db.ForeignKey('character.id'))
)

favorite_planet_association = db.Table(
    'planet_character',
    Base.metadata,
   db.Column('favorite_id', db.Integer, db.ForeignKey('favorite.id')),
   db.Column('planet_id', db.Integer, db.ForeignKey('planet.id'))
)

    
class Planet(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    planet_name = db.Column(db.String(80), unique=False)
    diameter = db.Column(db.Integer, unique=False)
    favorites = db.relationship('Favorite', secondary=favorite_planet_association, back_populates='planets')

    def __repr__(self):
        return '<Planets %r>' % self.planet_name

    def serialize(self):
        return {
            "id": self.id,
            "planet_name": self.planet_name,
            "diameter": self.diameter
            # do not serialize the password, its a security breach
        }

class Character(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    character_name =db.Column(db.String(80), unique=False)
    favorites = db.relationship('Favorite', secondary=favorite_character_association, back_populates='characters')

    def __repr__(self):
        return '<Characters %r>' % self.character_name

    def serialize(self):
        return {
            "character_name": self.id,
            # do not serialize the password, its a security breach
        }
    
class Favorite(db.Model):
    __tablename__ = 'favorite'
    id =db.Column(db.Integer, primary_key=True)
    user_id =db.Column(db.Integer, db.ForeignKey('user.id'))
    planets = db.relationship('Planet', secondary=favorite_planet_association, back_populates='favorites')
    characters = db.relationship('Character', secondary=favorite_character_association, back_populates='favorites')

    def __repr__(self):
        return '<Favorites %r>' % self.id

    def serialize(self):
        return {
            "id" : self.id,
            "user_id" : self.user_id,
            "planets" : self.planets,
            "characters" : self.characters
            # do not serialize the password, its a security breach
        }

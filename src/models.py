from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, declarative_base


db = SQLAlchemy()
Base = declarative_base()

# /db MODELS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password =db.Column(db.String(80), unique=False, nullable=False)
    is_active =db.Column(db.Boolean(), unique=False, nullable=False)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "favorites": self.favorites
            # do not serialize the password, its a security breach
        }
    
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    favorite_id = db.Column(db.Integer, nullable=False)
    favorite_type = db.Column(db.String(20), nullable=False)  # 'planet' or 'character'

    # Add unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'favorite_id', 'favorite_type'),)

    def serialize(self):
        return {
            "id" : self.id,
            "user_id" : self.user_id,
            "favorite_id" : self.favorite_id,
            "favorite_type" : self.favorite_type
        }

    def __repr__(self):
        return '<Favorite %r>' % self.id

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    diameter = db.Column(db.Float, nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter
        }
    
    def __repr__(self):
        return '<Planet %r>' % self.name
    

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def serialize(self):
        return {
            "name": self.name
        }

    def __repr__(self):
        return '<Character %r>' % self.name
    
    


       


import os
from sqlalchemy import Column, String, Integer, Float, create_engine
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

database_path = 'postgres://alex@localhost:5432/plant_survey_test'

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


'''
Plants
'''


class Plant(db.Model):
    __tablename__ = 'Plant'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    latin_name = Column(String(120), nullable=False)
    description = Column(String(2500), nullable=False)
    image_link = Column(String(500), nullable=False)
    plant_observations = db.relationship(
        'Observation', backref='plant', lazy=True)

    def __init__(self, name, latin_name, description, image_link):
        self.name = name
        self.latin_name = latin_name
        self.description = description
        self.image_link = image_link

    def __repr__(self):
        return f'<Plant {self.id} {self.name}>'
        # return f'<Hike {self.id}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'latin_name': self.latin_name,
            'description': self.description,
            'image_link': self.image_link
        }


'''
Plant Observations
'''


class Observation(db.Model):
    __tablename__ = 'Observations'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    date = Column(db.DateTime, nullable=False,
                  default=datetime.utcnow)
    plant_id = Column(Integer, db.ForeignKey(
        'Plant.id'), nullable=False)
    notes = Column(String(2500))
    # add GPS location?

    def __init__(self, name, date, plant_id, notes):
        self.name = name
        self.date = date
        self.plant_id = plant_id
        self.notes = notes

    def __repr__(self):
        return f'<Observation: Name {self.plant_id}, Date {self.date}, Plant ID {self.plant_id}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date,
            'plant_id': self.plant_id,
            'notes': self.notes,
        }

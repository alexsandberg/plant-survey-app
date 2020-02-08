import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

# set up environment variables using dotenv
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


database_path = os.getenv('DATABASE_URL')

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


# format datetime utility
def format_datetime(datetime):
    return "{:%B %d, %Y}".format(datetime)


# format plant_observations
def format_plant_observations(plant_observations):
    return [observation.format() for observation in plant_observations]


'''
Plants
'''


class Plant(db.Model):
    __tablename__ = 'Plant'

    id = Column(Integer, primary_key=True)
    username = Column(String(120), nullable=False)
    user_id = Column(String(120), nullable=False)
    name = Column(String(120), nullable=False)
    latin_name = Column(String(120), nullable=False)
    description = Column(String(2500), nullable=False)
    image_link = Column(String(500), nullable=False)
    plant_observations = db.relationship(
        'Observation', backref='plant', lazy=True)

    def __init__(self, username, user_id, name, latin_name, description, image_link):
        self.username = username
        self.user_id = user_id
        self.name = name
        self.latin_name = latin_name
        self.description = description
        self.image_link = image_link

    def __repr__(self):
        return f'<Plant {self.id} {self.name}>'

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
            'username': self.username,
            'user_id': self.user_id,
            'name': self.name,
            'latin_name': self.latin_name,
            'description': self.description,
            'image_link': self.image_link,
            'plant_observations':
                format_plant_observations(self.plant_observations)
        }


'''
Plant Observations
'''


class Observation(db.Model):
    __tablename__ = 'Observations'

    id = Column(Integer, primary_key=True)
    username = Column(String(120), nullable=False)
    user_id = Column(String(120), nullable=False)
    date = Column(db.DateTime, nullable=False,
                  default=datetime.utcnow)
    plant_id = Column(Integer, db.ForeignKey(
        'Plant.id'), nullable=False)
    notes = Column(String(2500))
    # add GPS location?

    def __init__(self, username, user_id, date, plant_id, notes):
        self.username = username
        self.user_id = user_id
        self.date = date
        self.plant_id = plant_id
        self.notes = notes

    def __repr__(self):
        return f'<Observation: Username {self.username}, Date {self.date}, Plant ID {self.plant_id}>'

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
            'username': self.username,
            'user_id': self.user_id,
            'datetime': self.date,
            'date': format_datetime(self.date),
            'plant_name': Plant.query.filter_by(id=self.plant_id).one_or_none().name,
            'plant_image': Plant.query.filter_by(id=self.plant_id).one_or_none().image_link,
            'plant_id': self.plant_id,
            'notes': self.notes,
        }

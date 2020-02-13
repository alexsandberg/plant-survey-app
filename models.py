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

# format plants


def format_plants(plants):
    return [plant.format() for plant in plants]


'''
Plants
'''


class Plant(db.Model):
    __tablename__ = 'Plants'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey(
        'Users.id'), nullable=False)
    name = Column(String(120), nullable=False)
    latin_name = Column(String(120), nullable=False)
    description = Column(String(2500), nullable=False)
    image_link = Column(String(500), nullable=False)
    plant_observations = db.relationship(
        'Observation', backref='plant', lazy=True)

    def __init__(self, user_id, name, latin_name, description, image_link):
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
    user_id = Column(Integer, db.ForeignKey(
        'Users.id'), nullable=False)
    date = Column(db.DateTime, nullable=False,
                  default=datetime.utcnow)
    plant_id = Column(Integer, db.ForeignKey(
        'Plants.id'), nullable=False)
    notes = Column(String(2500))

    def __init__(self, user_id, date, plant_id, notes):
        self.user_id = user_id
        self.date = date
        self.plant_id = plant_id
        self.notes = notes

    def __repr__(self):
        return f'<Observation: User ID {self.user_id}, Date {self.date}, Plant ID {self.plant_id}>'

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
            'user_id': self.user_id,
            'datetime': self.date,
            'date': format_datetime(self.date),
            'plant_name': Plant.query.filter_by(id=self.plant_id).one_or_none().name,
            'plant_image': Plant.query.filter_by(id=self.plant_id).one_or_none().image_link,
            'plant_id': self.plant_id,
            'notes': self.notes,
        }


'''
User
'''


class User(db.Model):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    username = Column(String(120), nullable=False)
    user_id = Column(String(120), nullable=False)
    date_added = Column(db.DateTime, nullable=False,
                        default=datetime.utcnow)
    role = Column(String(120), nullable=False)
    observations = db.relationship(
        'Observation', backref='user', lazy=True)
    plants = db.relationship(
        'Plant', backref='user', lazy=True)

    def __init__(self, name, username, user_id, date_added, role):
        self.name = name
        self.username = username
        self.user_id = user_id
        self.date_added = date_added
        self.role = role

    def __repr__(self):
        return f'<User: Name {self.name}, Username {self.username}, Date Added {self.date_added}, Role {self.role}>'

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
            'username': self.username,
            'user_id': self.user_id,
            'date_added': self.date_added,
            'date': format_datetime(self.date_added),
            'role': self.role,
            'observations':
                format_plant_observations(self.observations),
            'plants': format_plants(self.plants)
        }

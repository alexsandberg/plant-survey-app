import os
import datetime
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Plant, Observation, User


class PlantTestCase(unittest.TestCase):
    """This class represents the plant survey test case"""

    # auth tokens needed for successful testing
    ADMIN_ROLE_TOKEN = os.environ.get('ADMIN_ROLE_TOKEN')
    PUBLIC_ROLE_TOKEN = os.environ.get('PUBLIC_ROLE_TOKEN')

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "plant_survey_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # UTILITY METHODS

    # creates auth header with bearer token
    def create_auth_headers(self, token):
        # return auth headers using token
        return {
            "Authorization": "Bearer {}".format(
                token
            )}

    # creates test plant
    def create_test_plant(self, user_id):

        # create and insert new plant
        plant = Plant(user_id=user_id,
                      name=self.test_plant['name'],
                      latin_name=self.test_plant['latinName'],
                      description=self.test_plant['description'],
                      image_link=self.test_plant['imageLink'])
        plant.insert()

        return plant.id

    # creates new test observation
    def create_test_observation(self, plant_id, user_id):
        # create and insert new observation
        observation = Observation(user_id=user_id,
                                  date=self.test_observation['date'],
                                  plant_id=plant_id,
                                  notes=self.test_observation['notes'])
        observation.insert()

        return observation.id

    # creates new user for testing
    def create_test_user(user):
        # create and insert new user
        user = User(name=user['name'],
                    username=user['username'],
                    user_id=user['user_id'],
                    date_added=user['date_added'],
                    role=user['role'])

        user.insert()

        return user.id

    # deletes all entries from database
    def clear_database(self):
        # get and delete any plants and observations in database
        observations = Observation.query.all()
        for observation in observations:
            observation.delete()

        plants = Plant.query.all()
        for plant in plants:
            plant.delete()

    # generates random string
    def gen_random_string():
        return str(os.urandom(10))

    # sample plant for use in tests
    test_plant = {
        'name': gen_random_string(),
        'latinName': gen_random_string(),
        'description': gen_random_string(),
        'imageLink': gen_random_string()
    }

    # sample observation for use in tests
    test_observation = {
        'date': datetime.datetime.now(),
        'notes': gen_random_string()
    }

    # IDs for test users (already in database)
    ADMIN_ID = 1
    PUBLIC_ID = 27

    # PLANT tests

    def test_get_plant_failure(self):
        """Tests GET plants failure"""

        # ensure database is empty
        self.clear_database()

        # get response and load data
        response = self.client().get('/api/plants')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_plants(self):
        """Tests GET plants success"""

        # create a new plant to ensure database isn't empty
        self.create_test_plant(self.ADMIN_ID)

        # get response and load data
        response = self.client().get('/api/plants')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that data returned for plants
        self.assertTrue(data['plants'])

    def test_post_plant_success(self):
        """Tests POST new plant success"""

        # get headers using ADMIN token
        headers = self.create_auth_headers(token=self.ADMIN_ROLE_TOKEN)

        test_plant = self.test_plant
        test_plant['user_id'] = self.ADMIN_ID

        # get response and load data
        response = self.client().post('/api/plants/new', json=test_plant,
                                      headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_plant_failure(self):
        """Tests POST new plant failure"""

        # get headers using ADMIN token
        headers = self.create_auth_headers(token=self.ADMIN_ROLE_TOKEN)

        # get response with empty json and load data
        response = self.client().post('/api/plants/new', json={},
                                      headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_patch_plant_success(self):
        """Tests PATCH plant success"""

        # create a new plant to be updated and store plant id
        plant_id = self.create_test_plant(self.ADMIN_ID)

        # get headers using ADMIN token
        headers = self.create_auth_headers(token=self.ADMIN_ROLE_TOKEN)

        # set json data
        request_data = {
            'name': 'PATCH TEST',
            'latinName': None,
            'description': None,
            'imageLink': None
        }

        # get response with updated name json and load data
        response = self.client().patch('/api/plants/{}/edit'.format(plant_id),
                                       json=request_data,
                                       headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['plant']['name'], 'PATCH TEST')

    def test_patch_plant_failure(self):
        """Tests PATCH plant failure"""

        # create a new plant to be updated and store plant id
        plant_id = self.create_test_plant(self.ADMIN_ID)

        # get headers using ADMIN token
        headers = self.create_auth_headers(token=self.ADMIN_ROLE_TOKEN)

        # set malformed json data
        request_data = {
            'nome': 'PATCH TEST',
            'latinName': None,
            'description': None,
            'imageLink': None
        }

        # get response with malformed json and load data
        response = self.client().patch('/api/plants/{}/edit'.format(plant_id),
                                       json=request_data,
                                       headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_patch_or_delete_plant_not_found(self):
        """Tests 404 error for PATCH or DELETE plant"""

        # get headers using ADMIN token
        headers = self.create_auth_headers(token=self.ADMIN_ROLE_TOKEN)

        # DELETE
        # attempt to delete nonexisting plant and store response
        response = self.client().delete('/api/plants/1000/edit',
                                        headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

        # PATCH
        # attempt to patch nonexisting plant and store response
        response = self.client().patch('/api/plants/1000/edit',
                                       headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_plant_success(self):
        """Tests DELETE plant success"""

        # create a new plant to be deleted and store plant id
        plant_id = self.create_test_plant(self.ADMIN_ID)

        # get headers using ADMIN token
        headers = self.create_auth_headers(token=self.ADMIN_ROLE_TOKEN)

        # delete the plant and store response
        response = self.client().delete('/api/plants/{}/edit'.format(plant_id),
                                        headers=headers)
        data = json.loads(response.data)

        # check status code and success message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check if plant and name match deleted plant
        self.assertEqual(data['plant_name'], self.test_plant['name'])
        self.assertEqual(data['plant_id'], plant_id)

    # OBSERVATION tests

    def test_get_observations_failure(self):
        """Tests GET observations failure"""

        # ensure database is empty
        self.clear_database()

        # get response and load data
        response = self.client().get('/api/observations')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_observations_success(self):
        """Tests GET observations success"""

        # ensure database is not empty by adding a plant and observation

        # create a new plant and store plant id
        plant_id = self.create_test_plant(self.ADMIN_ID)

        # create and insert new observation using plant id
        self.create_test_observation(plant_id, self.PUBLIC_ID)

        # get response and load data
        response = self.client().get('/api/observations')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that data returned for observations
        self.assertTrue(data['observations'])

    def test_post_observation_success(self):
        """Tests POST observation success"""

        # get headers using PUBLIC token
        headers = self.create_auth_headers(token=self.PUBLIC_ROLE_TOKEN)

        # create new plant for observation
        plant_id = self.create_test_plant(self.ADMIN_ID)

        # create a new observation json using test plant
        observation = {
            'user_id': self.PUBLIC_ID,
            'date': self.test_observation['date'],
            'plantID': plant_id,
            'notes': self.test_observation['notes']
        }

        # get response and load data
        response = self.client().post('/api/observations/new',
                                      json=observation,
                                      headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_observation_failure(self):
        """Tests POST observation failure"""

        # get headers using PUBLIC token
        headers = self.create_auth_headers(token=self.PUBLIC_ROLE_TOKEN)

        # send request using test_observation, which is missing plant_id and user_id
        # get response and load data
        response = self.client().post('/api/observations/new',
                                      json=self.test_observation,
                                      headers=headers)

        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_patch_observation_success(self):
        """Tests PATCH observation success"""

        # create a new plant and store plant id
        plant_id = self.create_test_plant(self.ADMIN_ID)

        # create and insert new observation using plant id
        observation_id = self.create_test_observation(
            plant_id, self.PUBLIC_ID)

        # get headers using PUBLIC token
        headers = self.create_auth_headers(token=self.PUBLIC_ROLE_TOKEN)

        # set json data for observation patch with updated name
        request_data = {
            'date': None,
            'notes': 'PATCH TEST'
        }

        # get response with updated name json and load data
        response = self.client().patch('/api/observations/{}/edit'
                                       .format(observation_id),
                                       json=request_data,
                                       headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['observation']['notes'], 'PATCH TEST')

    def test_patch_observation_failure(self):
        """Tests PATCH observation failure"""

        # create a new plant and store plant id
        plant_id = self.create_test_plant(self.ADMIN_ID)

        # create and insert new observation using plant id
        observation_id = self.create_test_observation(
            plant_id, self.PUBLIC_ID)

        # get headers using PUBLIC token
        headers = self.create_auth_headers(token=self.PUBLIC_ROLE_TOKEN)

        # set malformed json data for observation patch - date key missing
        request_data = {
            'plantID': plant_id,
            'notes': None
        }

        # get response with updated name json and load data
        response = self.client().patch('/api/observations/{}/edit'
                                       .format(observation_id),
                                       json=request_data,
                                       headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_delete_observation_success(self):
        """Tests DELETE observation success"""

        # create a new plant and store plant id
        plant_id = self.create_test_plant(self.ADMIN_ID)

        # create and insert new observation using plant id
        observation_id = self.create_test_observation(
            plant_id, self.PUBLIC_ID)

        # get headers using PUBLIC token
        headers = self.create_auth_headers(token=self.PUBLIC_ROLE_TOKEN)

        # get response with updated name json and load data
        response = self.client().delete('/api/observations/{}/edit'
                                        .format(observation_id),
                                        headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check if id matches deleted observation
        self.assertEqual(data['observation_id'], observation_id)

    def test_patch_or_delete_observation_not_found(self):
        """Tests 404 not found error for PATCH or DELETE observation"""

        # get headers using PUBLIC token
        headers = self.create_auth_headers(token=self.PUBLIC_ROLE_TOKEN)

        # attempt to delete nonexisting observation and store response
        response = self.client().delete('/api/observations/1000/edit',
                                        headers=headers)

        # check status code
        self.assertEqual(response.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

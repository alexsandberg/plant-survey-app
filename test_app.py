import os
import base64
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Plant, Observation


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    # auth tokens needed for successful testing
    ADMIN_ROLE_TOKEN = os.environ.get('ADMIN_ROLE_TOKEN')
    PUBLIC_ROLE_TOKEN = os.environ.get('PUBLIC_ROLE_TOKEN')

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "plant_survey"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # sample plant for use in tests
        self.test_plant = {
            'name': 'Green whispy daffodil',
            'latinName': 'Veritus daffodilius',
            'description': 'Completely real plant that really exists, I promise.',
            'imageLink': '3https://images.homedepot-static.com/productImages/4e5bb2e3-fc4f-494c-8652-c2850918199e/svn/bloomsz-flower-bulbs-07589-64_1000.jpg'
        }

        # sample observation for use in tests
        self.test_observation = {
            'name': 'Alex Sandberg-Bernard',
            'date': '2020-01-14 16:26:40.400770',
            'notes': 'Sample notes'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def create_auth_headers(*args, **kwargs):

        # get token
        token = kwargs['token']

        # return auth headers
        return {
            "Authorization": "Bearer {}".format(
                # base64.b64encode()
                token
            )}

    # PLANT tests

    def test_get_plant_failure(self):
        """Tests GET plants failure"""

        # get and delete any plants and observations in database
        observations = Observation.query.all()
        for observation in observations:
            observation.delete()

        plants = Plant.query.all()
        for plant in plants:
            plant.delete()

        # get response and load data
        response = self.client().get('/plants')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_plants(self):
        """Tests GET plants success"""

        # create a new plant so database isn't empty
        plant = Plant(name=self.test_plant['name'],
                      latin_name=self.test_plant['latinName'],
                      description=self.test_plant['description'],
                      image_link=self.test_plant['imageLink'])
        plant.insert()

        # get response and load data
        response = self.client().get('/plants')
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

        # get response and load data
        response = self.client().post('/plants/new', json=self.test_plant,
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
        response = self.client().post('/plants/new', json={},
                                      headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_patch_plant_success(self):
        """Tests PATCH plant success"""

        # create a new plant to be updated
        plant = Plant(name=self.test_plant['name'],
                      latin_name=self.test_plant['latinName'],
                      description=self.test_plant['description'],
                      image_link=self.test_plant['imageLink'])
        plant.insert()

        # get the id of the new plant
        plant_id = plant.id

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
        response = self.client().patch('/plants/{}'.format(plant_id),
                                       json=request_data,
                                       headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['plant']['name'], 'PATCH TEST')

    def test_patch_plant_failure(self):
        """Tests PATCH plant failure"""

        # create a new plant to be updated
        plant = Plant(name=self.test_plant['name'],
                      latin_name=self.test_plant['latinName'],
                      description=self.test_plant['description'],
                      image_link=self.test_plant['imageLink'])
        plant.insert()

        # get the id of the new plant
        plant_id = plant.id

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
        response = self.client().patch('/plants/{}'.format(plant_id),
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
        response = self.client().delete('/plants/1000',
                                        headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

        # PATCH
        # attempt to patch nonexisting plant and store response
        response = self.client().patch('/plants/1000',
                                       headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_plant_success(self):
        """Tests DELETE plant success"""

        # create a new plant to be deleted
        plant = Plant(name=self.test_plant['name'],
                      latin_name=self.test_plant['latinName'],
                      description=self.test_plant['description'],
                      image_link=self.test_plant['imageLink'])
        plant.insert()

        # get the id of the new plant
        plant_id = plant.id

        # get headers using ADMIN token
        headers = self.create_auth_headers(token=self.ADMIN_ROLE_TOKEN)

        # delete the plant and store response
        response = self.client().delete('/plants/{}'.format(plant_id),
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

        # get response and load data
        response = self.client().get('/observations')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_observations_success(self):
        """Tests GET observations success"""

        # create new plant for observation
        plant = Plant(name=self.test_plant['name'],
                      latin_name=self.test_plant['latinName'],
                      description=self.test_plant['description'],
                      image_link=self.test_plant['imageLink'])
        plant.insert()

        # get the id of the new plant
        plant_id = plant.id

        # create a new observation so database isn't empty
        observation = Observation(name=self.test_observation['name'],
                                  date=self.test_observation['date'],
                                  plant_id=plant_id,
                                  notes=self.test_observation['notes'])
        observation.insert()

        # get response and load data
        response = self.client().get('/observations')
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
        plant = Plant(name=self.test_plant['name'],
                      latin_name=self.test_plant['latinName'],
                      description=self.test_plant['description'],
                      image_link=self.test_plant['imageLink'])
        plant.insert()

        # get the id of the new plant
        plant_id = plant.id

        # create a new observation json using plant
        observation = {
            'name': self.test_observation['name'],
            'date': self.test_observation['date'],
            'plantID': plant_id,
            'notes': self.test_observation['notes']
        }

        # get response and load data
        response = self.client().post('/observations',
                                      json=observation,
                                      headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

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

    # first test runs with empty database
    def no_plants_found_404(self):
        """Tests GET plants failure"""

        # get response and load data
        response = self.client().get('/plants')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # next test adds a plant
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

    def test_get_plants(self):
        """Tests GET plants success"""

        # get response and load data
        response = self.client().get('/plants')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that data returned for plants
        self.assertTrue(data['plants'])

    def test_patch_plant_success(self):
        """Tests PATCH plant success"""

        # get headers using ADMIN token
        headers = self.create_auth_headers(token=self.ADMIN_ROLE_TOKEN)

        # get response with updated name json and load data
        response = self.client().patch('/plants/19', json={'name': 'PATCH TEST'},
                                       headers=headers)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['plant']['name'], 'PATCH TEST')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Plant, Observation


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

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

    def test_get_plants(self):
        """Tests get plants success"""

        # get response and load data
        response = self.client().get('/plants')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that data returned for plants
        self.assertTrue(data['plants'])

    def test_405_plants_method_not_allowed(self):
        """Tests method not allowed 405"""

        # get response and load data
        response = self.client().post('/plants')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

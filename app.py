import os
from flask import Flask, request, abort, jsonify
from models import setup_db
from flask_cors import CORS
from models import Hike, Trail


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)

    # set up CORS, allowing all origins
    CORS(app, resources={'/': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        '''
        Sets access control.
        '''
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    return app


app = create_app()

if __name__ == '__main__':
    app.run()

import os
from flask import Flask, request, abort, jsonify, render_template, redirect
from models import setup_db
from flask_cors import CORS
from models import Plant, PlantInstance


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

    # ------------------------------------
    # ROUTES
    # ------------------------------------

    # home page route handler
    @app.route('/')
    def index():
        return render_template('pages/home.html')

    @app.route('/plants')
    def plants():

        # get all plants from database
        plants = Plant.query.all()

        plants_formatted = []

        # format each plant
        for plant in plants:
            plants_formatted.append(plant.format())

        # return plants
        return jsonify({
            'success': True,
            'plants': plants_formatted
        })

    return app


app = create_app()

if __name__ == '__main__':
    app.run()

import os
from flask import Flask, request, abort, jsonify, render_template, redirect
from models import setup_db
from flask_cors import CORS
from models import Plant, Observation


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
        # TODO build frontend
        pass

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

    @app.route('/plants/new', methods=['POST'])
    def new_plant():

        # load the request body
        body = request.get_json()

        # load data from body
        name = body.get('name')
        latin_name = body.get('latinName')
        description = body.get('description')
        image_link = body.get('imageLink')

        # ensure all fields have data
        if ((name is None) or (latin_name is None)
                or (description is None) or (image_link is None)):
            abort(422)

        # create a new plant
        plant = Plant(name=name, latin_name=latin_name,
                      description=description, image_link=image_link)

        try:
            # add plant to the database
            plant.insert()
        except Exception as e:
            print('ERROR: ', str(e))
            abort(422)

        # return plant if success
        return jsonify({
            "success": True,
            "plant": plant.format()
        })

    @app.route('/plants/<int:id>', methods=['PATCH', 'DELETE'])
    def edit_or_delete_plant(id):

        # if PATCH
        if request.method == 'PATCH':

            # get plant by id
            plant = Plant.query.filter_by(id=id).one_or_none()

            # get request body
            body = request.get_json()

            # update plant with data from body
            if body.get('name'):
                plant.name = body.get('name')

            if body.get('latinName'):
                plant.latin_name = body.get('latinName')

            if body.get('description'):
                plant.description = body.get('description')

            if body.get('imageLink'):
                plant.image_link = body.get('imageLink')

            try:
                # update plant in database
                plant.insert()
            except Exception as e:
                print('ERROR: ', str(e))
                abort(422)

            # return plant if success
            return jsonify({
                "success": True,
                "plant": plant.format()
            })

        # if DELETE
        if request.method == 'DELETE':

            # get plant by id
            plant = Plant.query.filter_by(id=id).one_or_none()

            # save plant name
            plant_name = plant.name

            try:
                # delete plant from the database
                plant.delete()
            except Exception as e:
                print('ERROR: ', str(e))
                abort(422)

            # return plant name if successfully deleted
            return jsonify({
                "success": True,
                "plant_name": plant_name
            })

    @app.route('/observations', methods=['GET', 'POST'])
    def plant_observations():

        # POST REQUESTS
        if request.method == 'POST':
            # load the request body
            body = request.get_json()

            # load data from body
            name = body.get('name')
            date = body.get('date')
            plant_id = body.get('plantID')
            notes = body.get('notes')

            # ensure required fields have data
            if ((name is None) or (date is None)
                    or (plant_id is None)):
                abort(422)

            # create a new plant
            observation = Observation(
                name=name, date=date, plant_id=plant_id, notes=notes)

            try:
                # add observation to the database
                observation.insert()
            except Exception as e:
                print('ERROR: ', str(e))
                abort(422)

            # return observation if success
            return jsonify({
                "success": True,
                "observation": observation.format()
            })

        # GET REQUESTS
        else:
            # get all plant observations
            observations = Observation.query.all()

            # if no observations
            if not observations:
                abort(404)

            observations_formatted = []

            # format each plant
            for observation in observations:
                observations_formatted.append(observation.format())

            # return plants
            return jsonify({
                'success': True,
                'observations': observations_formatted
            })

    return app


app = create_app()

if __name__ == '__main__':
    app.run()

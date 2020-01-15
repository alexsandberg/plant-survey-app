import os
from flask import Flask, request, abort, jsonify, render_template, redirect
from models import setup_db
from flask_cors import CORS

from models import Plant, Observation
from auth.auth import AuthError, requires_auth


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

        # 404 if no plants found
        if len(plants) == 0:
            abort(404)

        plants_formatted = []

        # format each plant
        for plant in plants:

            # get plant observations
            observations = plant.plant_observations

            # format plan
            plant = plant.format()

            plant_observations = []

            # format each observation
            for observation in observations:
                plant_observations.append(observation.format())

            # add formatted observations to formatted plant
            plant['plant_observations'] = plant_observations

            plants_formatted.append(plant)

        # return plants
        return jsonify({
            'success': True,
            'plants': plants_formatted
        })

    @app.route('/plants/new', methods=['POST'])
    @requires_auth('post:plants')
    def new_plant(jwt):

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
    @requires_auth('edit_or_delete:plants')
    def edit_or_delete_plant(*args, **kwargs):

        # get id from kwargs
        id = kwargs['id']

        # get plant by id
        plant = Plant.query.filter_by(id=id).one_or_none()

        # abort 404 if no plant found
        if plant is None:
            abort(404)

        # if PATCH
        if request.method == 'PATCH':

            # get request body
            body = request.get_json()

            # get all keys from request body
            body_keys = []
            for key in body:
                body_keys.append(key)

            # make sure correct keys are present
            if sorted(body_keys) != sorted(['name', 'latinName', 'description',
                                            'imageLink']):
                abort(422)

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

            # save plant name and id
            plant_name = plant.name
            plant_id = plant.id

            try:
                # delete plant from the database
                plant.delete()
            except Exception as e:
                print('ERROR: ', str(e))
                abort(422)

            # return plant name if successfully deleted
            return jsonify({
                "success": True,
                "plant_name": plant_name,
                "plant_id": plant_id
            })

    @app.route('/observations')
    def get_plant_observations():

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

    @app.route('/observations', methods=['POST'])
    @requires_auth('post:observations')
    def post_plant_observation(jwt):
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

    @app.route('/observations/<int:id>', methods=['PATCH', 'DELETE'])
    @requires_auth('edit_or_delete:observations')
    def edit_or_delete_observation(*args, **kwargs):

        # get id from kwargs
        id = kwargs['id']

        # get observation by id
        observation = Observation.query.filter_by(id=id).one_or_none()

        # if PATCH
        if request.method == 'PATCH':

            # get request body
            body = request.get_json()

            # get all keys from request body
            body_keys = []
            for key in body:
                body_keys.append(key)

            # make sure correct keys are present
            if sorted(body_keys) != sorted(['name', 'date', 'plantID',
                                            'notes']):
                abort(422)

            # update observation with data from body
            if body.get('name'):
                observation.name = body.get('name')

            if body.get('date'):
                observation.date = body.get('date')

            if body.get('plantID'):
                observation.plant_id = body.get('plantID')

            if body.get('notes'):
                observation.notes = body.get('notes')

            try:
                # update observation in database
                observation.insert()
            except Exception as e:
                print('ERROR: ', str(e))
                abort(422)

            # return observation if success
            return jsonify({
                "success": True,
                "observation": observation.format()
            })

        # if DELETE
        if request.method == 'DELETE':

            # save observation name and id
            observation_name = observation.name
            observation_id = observation.id

            try:
                # delete observation from the database
                observation.delete()
            except Exception as e:
                print('ERROR: ', str(e))
                abort(422)

            # return success
            return jsonify({
                "success": True,
                "observation_name": observation_name,
                "observation_id": observation_id
            })

    # Error Handling
    '''
    Error handling for unprocessable entity
    '''
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    '''
    Error handling for resource not found
    '''
    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    '''
    Error handling for method not allowed
    '''
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    '''
    Error handling for bad request
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    '''
    Error handling for AuthError
    '''
    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    return app


app = create_app()

if __name__ == '__main__':
    app.run()

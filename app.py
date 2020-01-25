from flask import Flask, request, abort, jsonify, render_template, redirect, url_for, session
import json
from models import setup_db
from flask_cors import CORS
from os import environ as env
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
from models import Plant, Observation
from auth.auth import AuthError, requires_auth, create_login_link
import constants
from dotenv import load_dotenv, find_dotenv


def create_app(test_config=None):

    # set up environment variables using dotenv
    ENV_FILE = find_dotenv()
    if ENV_FILE:
        load_dotenv(ENV_FILE)

    # set up Auth0
    AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
    AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
    AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
    AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
    AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
    AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)

    # set up Flask app
    app = Flask(__name__)
    setup_db(app)
    app.secret_key = constants.SECRET_KEY

    # set up OAuth
    oauth = OAuth(app)
    auth0 = oauth.register(
        'auth0',
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        api_base_url=AUTH0_BASE_URL,
        access_token_url=AUTH0_BASE_URL + '/oauth/token',
        authorize_url=AUTH0_BASE_URL + '/authorize',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )

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

    # AUTH ROUTES -- AUTH0 BOILERPLATE

    @app.route('/callback')
    def callback_handling():
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        session[constants.JWT_PAYLOAD] = userinfo
        session[constants.PROFILE_KEY] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }
        return redirect('/dashboard')

    @app.route('/login')
    def login():
        return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL,
                                        audience=AUTH0_AUDIENCE)

    @app.route('/logout')
    def logout():
        session.clear()
        params = {'returnTo': url_for(
            'home', _external=True), 'client_id': AUTH0_CLIENT_ID}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

    @app.route('/dashboard')
    def dashboard():
        return render_template('/pages/dashboard.html',
                               userinfo=session[constants.PROFILE_KEY],
                               userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))

    # ------------------------------------
    # ROUTES
    # ------------------------------------

    # home page route handler
    @app.route('/')
    def home():

        # add login link function to jinja context
        app.jinja_env.globals.update(create_login_link=create_login_link)

        return render_template('pages/home.html'), 200

    @app.route('/plants')
    def plants():
        '''
        Handles GET requests for getting all plants.
        '''

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
        return render_template('pages/plants.html',
                               plants=plants_formatted), 200
        # return plants
        # return jsonify({
        #     'success': True,
        #     'plants': plants_formatted
        # })

    @app.route('/plants/<int:id>')
    def get_plant_by_id(*args, **kwargs):
        # get id from kwargs
        id = kwargs['id']

        # get plant by id
        plant = Plant.query.filter_by(id=id).one_or_none()

        # abort 404 if no plant found
        if plant is None:
            abort(404)

        # serve plant page with formatted plant
        return render_template('pages/plant.html',
                               plant=plant.format()), 200

    @app.route('/plants', methods=['POST'])
    @requires_auth('post:plants')
    def new_plant(jwt):
        '''
        Handles POST requests for adding new plant.
        '''

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
        '''
        Handles PATCH and DELETE requests for plants.
        '''

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
        '''
        Handles GET requests for getting all observations.
        '''

        # get all plant observations
        observations = Observation.query.all()

        # if no observations
        if not observations:
            abort(404)

        observations_formatted = []

        # format each observation
        for observation in observations:
            observations_formatted.append(observation.format())

        # return observations
        return render_template('pages/observations.html',
                               observations=observations_formatted), 200
        # return jsonify({
        #     'success': True,
        #     'observations': observations_formatted
        # })

    @app.route('/observations', methods=['POST'])
    @requires_auth('post:observations')
    def post_plant_observation(jwt):
        '''
        Handles POST requests for adding new observation.
        '''

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
        '''
        Handles PATCH and DELETE requests for observations.
        '''

        # get id from kwargs
        id = kwargs['id']

        # get observation by id
        observation = Observation.query.filter_by(id=id).one_or_none()

        # abort 404 if no observation found
        if observation is None:
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

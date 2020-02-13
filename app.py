from flask import Flask, flash, request, abort, jsonify, render_template, redirect, url_for, session
from functools import wraps
from models import setup_db, Plant, Observation, User
from flask_cors import CORS
from os import environ as env
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
from auth.auth import AuthError, requires_auth, create_login_link
import constants
import json
from dotenv import load_dotenv, find_dotenv
import requests
from datetime import datetime


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
            'scope': 'openid profile email preferred_username',
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
                             'GET,PUT,PATCH,POST,DELETE,OPTIONS')
        return response

    def login_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if 'logged_in' in session:
                return f(*args, **kwargs)
            else:
                flash('You need to login first')
                return redirect(url_for('home'))
        return wrap

    # add login link function to jinja context
    app.jinja_env.globals.update(create_login_link=create_login_link)

    # UTILITY FUNCTIONS

    # plant formatting
    def format_plants(plants):
        return [plant.format() for plant in plants]

    # observation formatting

    def format_observations(observations):
        return [observation.format() for observation in observations]

    # get Auth0 management API token
    def get_mgmt_token():

        data = {
            'grant_type': 'client_credentials',
            'client_id': AUTH0_CLIENT_ID,
            'client_secret': AUTH0_CLIENT_SECRET,
            'audience': 'https://plant-survey.auth0.com/api/v2/'
        }

        resp = requests.post('https://plant-survey.auth0.com/oauth/token',
                             data=data,
                             headers={'content-type': 'application/x-www-form-urlencoded'})
        info = resp.json()
        mgmt_token = info['access_token']

        return mgmt_token

    # check if user is in database
    def check_if_user_exists(user_id):

        # look in Users table for user
        user = User.query.filter_by(user_id=user_id).one_or_none()

        # if user not found return false
        if user is None:
            return False
        else:
            return True

    # add 'Public' role to user
    def add_public_role(user_id, mgmt_token):

        # Auth0 public role ID
        PUBLIC_ROLE_ID = 'rol_X9T29OUlO7kYdItp'

        # request body
        data = {
            "roles": [
                PUBLIC_ROLE_ID
            ]
        }

        # call management API with user_id and role
        role_resp = requests.post(f'https://plant-survey.auth0.com/api/v2/users/{user_id}/roles',
                                  headers={
                                      'Authorization': f"Bearer {mgmt_token}"},
                                  json=data)

        # raises exception for any 4xx or 5xx errors
        role_resp.raise_for_status()

    # add user if not in database

    def create_new_user(user):
        print('NEW USER: ', user)

        # create new user
        new_user = User(name=user['name'],
                        username=user['username'],
                        user_id=user['user_id'],
                        date_added=user['date_added'],
                        role=user['role'])

        try:
            # insert new user in Users table
            new_user.insert()
        except Exception as e:
            print('ERROR: ', str(e))
            abort(422)

        return new_user.id

    # AUTH ROUTES -- AUTH0 BOILERPLATE

    @app.route('/callback')
    def callback_handling():
        token = auth0.authorize_access_token()
        # print('TOKEN: ', token['access_token'])

        # get user info and store user id
        resp = auth0.get('userinfo')
        userinfo = resp.json()
        user_id = userinfo['sub']
        # print('ID: ', user_id)

        # store user info
        user = {
            'user_id': user_id
        }

        # check if user exists in Users table
        if check_if_user_exists(user_id):

            # get user info from Users table
            user_table_id = User.query.filter_by(
                user_id=user_id).one_or_none().id
            name = User.query.filter_by(user_id=user_id).one_or_none().name
            username = User.query.filter_by(
                user_id=user_id).one_or_none().username
            date_added = User.query.filter_by(
                user_id=user_id).one_or_none().date_added
            role = User.query.filter_by(user_id=user_id).one_or_none().role

            # add to user info
            user['user_table_id'] = user_table_id
            user['name'] = name
            user['username'] = username
            user['date_added'] = date_added
            user['role'] = role

        # if no, create new user
        else:
            # get management API token
            mgmt_token = get_mgmt_token()
            # print('MGMT TOKEN: ', mgmt_token)

            # set new user role to 'Public' on Auth0
            add_public_role(user_id, mgmt_token)
            user['role'] = 'Public'

            # get additional user info from management api
            user_resp = requests.get(f'https://plant-survey.auth0.com/api/v2/users/{user_id}',
                                     headers={'Authorization': f"Bearer {mgmt_token}"})
            id_info = user_resp.json()

            # get username from response
            if 'username' in id_info:
                username = id_info['username']
            elif 'name' in id_info:
                username = id_info['name']
            else:
                username = id_info['email']

            user['username'] = username
            user['name'] = id_info['name']

            # set date added to now
            user['date_added'] = datetime.utcnow()

            # add new user to Users table, save user_table_id
            user_table_id = create_new_user(user)
            user['user_table_id'] = user_table_id

        # add session variables
        session['logged_in'] = True
        session[constants.JWT_PAYLOAD] = userinfo
        session[constants.JWT] = token['access_token']
        session[constants.PROFILE_KEY] = user

        print('SESSION PROFILE: ', session)

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

    # ------------------------------------
    # ROUTES
    # ------------------------------------

    @app.route('/dashboard')
    @login_required
    def dashboard():

        # # if no active jwt, redirect to home login page
        # if 'jwt_payload' not in session:
        #     return render_template('pages/login.html'), 200

        # get user from Users table
        user_table_id = User.query.filter_by(
            user_id=session['profile']['user_id']).one_or_none().id

        # get all plants and observations that match user
        plants = Plant.query.filter_by(
            user_id=user_table_id).all()
        observations = Observation.query.filter_by(
            user_id=user_table_id).all()

        # format all plants and observations
        if (len(plants) != 0):
            plants = format_plants(plants)

        if (len(observations) != 0):
            observations = format_observations(observations)

        return render_template('/pages/dashboard.html',
                               userinfo=session[constants.PROFILE_KEY],
                               plants=plants,
                               observations=observations)

    # home page route handler
    @app.route('/')
    def home():

        return redirect('plants')

    @app.route('/plants')
    def plants():
        '''
        Handles GET requests for getting all plants.
        '''

        # get all plants from API
        response = get_plants_api()
        data = json.loads(response.data)
        plants = data['plants']

        # return template with plants
        return render_template('pages/plants.html',
                               plants=plants), 200

    @app.route('/plants/<int:id>')
    def get_plant_by_id(id):

        # get plant by id from API
        response = get_plant_by_id_api(id)
        data = json.loads(response.data)
        plant = data['plant']

        # serve plant page with plant result
        return render_template('pages/plant.html',
                               plant=plant), 200

    @app.route('/plants/new')
    @login_required
    @requires_auth('post:plants')
    def new_plant_form(jwt):
        '''
        Handles GET requests for new plant form page.
        '''
        # return new plant form
        return render_template('forms/new_plant.html'), 200

    @app.route('/plants/<int:id>/edit')
    @login_required
    @requires_auth('edit_or_delete:plants')
    def get_edit_plant_form(*args, **kwargs):
        '''
        Handles GET requests for edit plant form.
        '''

        # get id from kwargs
        id = kwargs['id']

        # get plant by id
        plant = Plant.query.filter_by(id=id).one_or_none()

        # return edit plant template with plant info
        return render_template('forms/edit_plant.html',
                               plant=plant.format()), 200

    @app.route('/observations')
    def get_plant_observations():
        '''
        Handles GET requests for getting all observations.
        '''

        # get all plant observations from API
        response = get_observations_api()
        data = json.loads(response.data)
        observations = data['observations']

        # return template with observations
        return render_template('pages/observations.html',
                               observations=observations), 200

    @app.route('/observations/new')
    @login_required
    @requires_auth('post:observations')
    def new_observation_form(jwt):
        '''
        Handles GET requests for new plant form page.
        '''

        # redirect to observations if plant id not included
        if 'plant' not in request.args:
            return redirect('/observations')

        # get args from request
        plant_id = request.args.get('plant')

        # get plant by id
        plant = Plant.query.filter_by(id=plant_id).one_or_none()

        # abort 404 if not found
        if plant is None:
            abort(404)

        # return new plant form
        return render_template('forms/new_observation.html',
                               plant=plant.format()), 200

    @app.route('/observations/<int:id>/edit')
    @login_required
    @requires_auth('edit_or_delete:observations')
    def get_edit_observation_form(*args, **kwargs):
        '''
        Handles GET requests for edit observation form.
        '''

        # get id from kwargs
        id = kwargs['id']

        # get plant by id
        observation = Observation.query.filter_by(id=id).one_or_none()

        # return edit plant template with plant info
        return render_template('forms/edit_observation.html',
                               observation=observation.format()), 200

    # API ROUTES

    @app.route('/api/plants')
    def get_plants_api():
        '''
        Handles API GET requests for getting all plants. Returns JSON.
        '''

        # get all plants from database
        plants = Plant.query.all()

        # 404 if no plants found
        if len(plants) == 0:
            abort(404)

        # format each plant
        plants = format_plants(plants)

        # return plants
        return jsonify({
            'success': True,
            'plants': plants
        })

    @app.route('/api/plants/<int:id>')
    def get_plant_by_id_api(id):
        '''
        Handles API GET requests for getting plant by ID. Returns JSON.
        '''

        # get plant by ID
        plant = Plant.query.filter_by(id=id).one_or_none()

        # 404 if no plants found
        if plant is None:
            abort(404)

        # return formatted plant
        return jsonify({
            'success': True,
            'plant': plant.format()
        })

    @app.route('/api/plants/new', methods=['POST'])
    @requires_auth('post:plants')
    def new_plant_api(jwt):

        # get request body
        body = request.get_json()

        # get user table id from session
        user_id = session['profile']['user_table_id']

        # load plant form data
        name = body.get('name')
        latin_name = body.get('latinName')
        description = body.get('description')
        image_link = body.get('imageLink')

        # ensure all fields have data
        if ((name == "") or (latin_name == "")
                or (description == "") or (image_link == "")):
            abort(422)

        # create a new plant
        plant = Plant(user_id=user_id, name=name,
                      latin_name=latin_name, description=description,
                      image_link=image_link)

        try:
            # add plant to the database
            plant.insert()
        except Exception as e:
            print('ERROR: ', str(e))
            abort(422)

        # flash success message
        flash(f'Plant {name} successfully created!')

        return jsonify({
            'success': True,
            'plant': plant.format()
        })

    @app.route('/api/plants/<int:id>/edit', methods=['PATCH', 'DELETE'])
    @requires_auth('edit_or_delete:plants')
    def edit_or_delete_plant_api(*args, **kwargs):
        '''
        Handles API PATCH and DELETE requests for plants.
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

            # flash success message
            flash(f'Plant {plant.name} successfully updated.')

            # return plant if success
            return jsonify({
                "success": True,
                "plant": plant.format()
            })

        # if DELETE
        if request.method == 'DELETE':

            # save plant name
            plant_name = plant.name

            # first delete all observations related to plant
            observations = Observation.query.filter_by(plant_id=id).all()
            for observation in observations:
                observation.delete()

            try:
                # delete plant from the database
                plant.delete()
            except Exception as e:
                print('ERROR: ', str(e))
                abort(422)

            # flash success message
            flash(f'Plant {plant_name} successfully deleted.')

            # return if successfully deleted
            return jsonify({
                "success": True,
                "plant_name": plant_name,
                "plant_id": id
            })

    @app.route('/api/observations')
    def get_observations_api():
        '''
        Handles API GET requests for getting all observations. Returns JSON.
        '''

        # get all observations from database
        observations = Observation.query.all()

        # 404 if no observations found
        if len(observations) == 0:
            abort(404)

        # format each observation
        observations = format_observations(observations)

        # return observations
        return jsonify({
            'success': True,
            'observations': observations
        })

    @app.route('/api/observations/<int:id>')
    def get_observation_by_id_api(id):
        '''
        Handles API GET requests for getting observation by id. Returns JSON.
        '''

        # get observation from database by id
        observation = Observation.query.filter_by(id=id).one_or_none()

        # 404 if no observation found
        if observation is None:
            abort(404)

        # return formatted observation
        return jsonify({
            'success': True,
            'observation': observation.format()
        })

    @app.route('/api/observations/new', methods=['POST'])
    @requires_auth('post:observations')
    def post_plant_observation_api(jwt):
        '''
        Handles API POST requests for adding new observation.
        '''

        # get request body
        body = request.get_json()

        # get user table id from session
        user_id = session['profile']['user_table_id']

        # load observation body data
        plant_id = body.get('plantID')
        date = body.get('date')
        notes = body.get('notes')

        # ensure required fields have data
        if ((date == '') or (plant_id == '')):
            abort(422)

        # create a new observation
        observation = Observation(user_id=user_id, date=date,
                                  plant_id=plant_id, notes=notes)

        try:
            # add observation to the database
            observation.insert()
        except Exception as e:
            print('ERROR: ', str(e))
            abort(422)

        # flash success message
        flash('Observation successfully created!')

        # return observation
        return jsonify({
            'success': True,
            'observation': observation.format()
        })

    @app.route('/api/observations/<int:id>/edit', methods=['PATCH', 'DELETE'])
    @requires_auth('edit_or_delete:observations')
    def edit_or_delete_observation_api(*args, **kwargs):
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
            if sorted(body_keys) != sorted(['date', 'notes']):
                abort(422)

            # update observation with data from body
            if body.get('date'):
                observation.date = body.get('date')

            if body.get('notes'):
                observation.notes = body.get('notes')

            try:
                # update observation in database
                observation.insert()
            except Exception as e:
                print('ERROR: ', str(e))
                abort(422)

            # flash success message
            flash('Observation successfully updated!')

            # return observation if success
            return jsonify({
                "success": True,
                "observation": observation.format()
            })

        # if DELETE
        if request.method == 'DELETE':

            # save observation id
            observation_id = observation.id

            try:
                # delete observation from the database
                observation.delete()
            except Exception as e:
                print('ERROR: ', str(e))
                abort(422)

            # flash success message
            flash('Observation successfully deleted!')

            # return success
            return jsonify({
                "success": True,
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
        message = ex.error['description']
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        print('AUTH ERROR: ', response.get_data(as_text=True))
        flash(f'{message} Please login.')
        return redirect('/')

    return app


app = create_app()

if __name__ == '__main__':
    app.run()

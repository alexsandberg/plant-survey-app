from flask import Flask, flash, request, abort, jsonify, render_template, redirect, url_for, session
from functools import wraps
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

    # UTILITY –– plant and observation formatting

    def format_plants(plants):
        return [plant.format() for plant in plants]

    def format_observations(observations):
        return [observation.format() for observation in observations]

    # AUTH ROUTES -- AUTH0 BOILERPLATE

    @app.route('/callback')
    def callback_handling():
        token = auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        session['logged_in'] = True
        session[constants.JWT_PAYLOAD] = userinfo
        session[constants.JWT] = token['access_token']
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
        # session.pop('logged_in', None)
        session.clear()
        params = {'returnTo': url_for(
            'home', _external=True), 'client_id': AUTH0_CLIENT_ID}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

    # ------------------------------------
    # ROUTES
    # ------------------------------------

    @app.route('/dashboard')
    def dashboard():

        # if no active jwt, redirect to home login page
        if 'jwt_payload' not in session:
            return redirect('/')

        contributor_email = session['jwt_payload']['email']

        # get all plants and observations that match user email
        plants = Plant.query.filter_by(
            contributor_email=contributor_email).all()
        observations = Observation.query.filter_by(
            contributor_email=contributor_email).all()

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

        # for plant in plants:
        #     print(
        #         'PLANT: \n'
        #         '{'
        #         f'"contributorEmail": "{plant.contributor_email}",'
        #         f'"name": "{plant.name}",'
        #         f'"latinName": "{plant.latin_name}",'
        #         f'"description": "{plant.description}",'
        #         f'"imageLink": "{plant.image_link}"'
        #         '}'
        #     )

        # 404 if no plants found
        if len(plants) == 0:
            abort(404)

        # format each plant
        plants = format_plants(plants)

        # return plants
        return render_template('pages/plants.html',
                               plants=plants), 200

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

    @app.route('/plants/new')
    @login_required
    def new_plant_form():
        '''
        Handles GET requests for new plant form page.
        '''
        # return new plant form
        return render_template('forms/new_plant.html'), 200

    @app.route('/plants/new', methods=['POST'])
    @requires_auth('post:plants')
    @login_required
    def new_plant(jwt):
        '''
        Handles POST requests for adding new plant.
        '''

        # load plant form data
        name = request.form['name']
        latin_name = request.form['latin_name']
        description = request.form['description']
        image_link = request.form['image_link']

        # load contributor email from session
        contributor_email = session['jwt_payload']['email']

        # ensure all fields have data
        if ((contributor_email is None) or (name == "") or (latin_name == "")
                or (description == "") or (image_link == "")):
            abort(422)

        # create a new plant
        plant = Plant(contributor_email=contributor_email, name=name,
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

        # return redirect to dashboard
        return redirect('/dashboard')

    @app.route('/plants/<int:id>/edit')
    @requires_auth('edit_or_delete:plants')
    @login_required
    def get_edit_plant_form(*args, **kwargs):
        '''
        Handles GET requests for edit plant form.
        '''

        # get id from kwargs
        id = kwargs['id']

        # get plant by id
        plant = Plant.query.filter_by(id=id).one_or_none()

        # return edit plant template with plant info
        return render_template('forms/edit_plant.html', plant=plant.format()), 200

    @app.route('/plants/<int:id>/edit', methods=['PATCH', 'DELETE'])
    @requires_auth('edit_or_delete:plants')
    @login_required
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
            # contributor_email is not allowed to be updated
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
                "success": True
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
                "success": True
            })

    @app.route('/observations')
    def get_plant_observations():
        '''
        Handles GET requests for getting all observations.
        '''

        # get all plant observations
        observations = Observation.query.all()

        # for observation in observations:
        #     print(
        #         'OBSERVATION: \n'
        #         '{'
        #         f'"contributorEmail": "{observation.contributor_email}",'
        #         f'"name": "{observation.name}",'
        #         f'"date": "{observation.date}",'
        #         f'"plantID": {observation.plant_id},'
        #         f'"notes": "{observation.notes}"'
        #         '}'
        #     )

        # if no observations
        if not observations:
            abort(404)

        # format each observation
        observations = format_observations(observations)

        # return observations
        return render_template('pages/observations.html',
                               observations=observations), 200

    @app.route('/observations/new')
    @login_required
    def new_observation_form():
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

    @app.route('/observations/new', methods=['POST'])
    @requires_auth('post:observations')
    @login_required
    def post_plant_observation(jwt):
        '''
        Handles POST requests for adding new observation.
        '''

        # load data from request and session
        contributor_email = session['jwt_payload']['email']
        plant_id = request.args.get('plant')
        name = request.form['name']
        date = request.form['date']
        notes = request.form['notes']

        # ensure required fields have data
        if ((contributor_email is None) or (name == '') or (date == '')
                or (plant_id == '')):
            abort(422)

        # create a new plant
        observation = Observation(contributor_email=contributor_email,
                                  name=name, date=date, plant_id=plant_id,
                                  notes=notes)

        try:
            # add observation to the database
            observation.insert()
        except Exception as e:
            print('ERROR: ', str(e))
            abort(422)

        # flash success message
        flash('Observation successfully created!')

        # return redirect to dashboard
        return redirect('/dashboard')

    @app.route('/observations/<int:id>', methods=['PATCH', 'DELETE'])
    @requires_auth('edit_or_delete:observations')
    @login_required
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
            # contributor_email is not allowed to be updated
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

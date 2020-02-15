# Colorado Rare Plant Survey Application

## Udacity Full Stack Nanodegree - Capstone Project

This application is a citizen science tool for surveying rare plants in Colorado. Anyone can create a public account and record observations of rare plants they find while exploring Colorado's beautiful natural areas. These observations will help inform vital conservation efforts. Scientists and researchers with admin credentials can create and update listings of additional plants, adding to the database of plant species.

This tool is the capstone project for the [Udacity Full Stack Web Developer Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044), and it is intended to demonstrate proficiency in the following areas: 

* Data modeling
    * Architect relational database models in Python
    * Utilize SQLAlchemy to conduct database queries
* API Architecture and Testing
    * Follow RESTful principles of API development using Flask
    * Structure endpoints to perform CRUD operations, as well as error handling
    * Demonstrate validity of API behavior using the unittest library
* Third Party Authentication
    * Configure Role Based Authentication and roles-based access control (RBAC) in a Flask application utilizing Auth0
    * Decode and verify JWTs from Authorization headers
* Deployment
    * API is [hosted live via Heroku](https://plant-survey-tool.herokuapp.com/)


## API Reference

### Getting Started

* Base URL: Plant and observations data can be accessed directly through the API, using the base URL `https://plant-survey-tool.herokuapp.com/api`. Alternatively, utilize the frontend at [https://plant-survey-tool.herokuapp.com/](https://plant-survey-tool.herokuapp.com/).
* Authentication: Most endpoints require either Public or Admin permissions. Navigate to [https://plant-survey-tool.herokuapp.com/api/key](https://plant-survey-tool.herokuapp.com/api/key) and create an account or sign in to obtain an API key. Default authorization is "Public".

### Error Handling

Errors are returned as JSON in the following format:<br>

    {
        "success": False,
        "error": 404,
        "message": "resource not found"
    }

The API will return the following types of errors:

* 400 – bad request
* 401 – unauthorized
* 404 – resource not found
* 405 – method not allowed
* 422 – unprocessable

### Endpoints

#### GET /plants

* General:
  * Returns a list plants with associated observations.
  * Does not require authorization.
* Sample request: 
    ```bash
    curl https://plant-survey-tool.herokuapp.com/api/plants
    ```
* Sample response:
    ```
    {
        "plants": [
            {
                "description": "A squat, globular, spiny succulent. Each mature stem is 3-12 cm tall, 4-9 cm wide; the largest observed was 24 cm tall x 14 cm wide. However, during the driest part of the year the stem may shrink to below ground-level. Central spines are straight (hookless). The plants are inconspicuous except when in flower (April-May), when showy, fragrant, pink to magenta flowers appear at the top of the stem.",
                "id": 6,
                "image_link": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_16984.jpg",
                "latin_name": "Sclerocactus glaucus",
                "name": "Colorado hookless cactus",
                "plant_observations": [
                    {
                        "date": "June 21, 2018",
                        "datetime": "Thu, 21 Jun 2018 11:11:00 GMT",
                        "id": 7,
                        "notes": "Seen near Glenwood Springs.",
                        "plant_id": 6,
                        "plant_image": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_16984.jpg",
                        "plant_name": "Colorado hookless cactus",
                        "user_id": 27
                    },
                    {
                        "date": "June 10, 2018",
                        "datetime": "Sun, 10 Jun 2018 16:26:00 GMT",
                        "id": 10,
                        "notes": "Saw several on trail outside Grand Junction.",
                        "plant_id": 6,
                        "plant_image": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_16984.jpg",
                        "plant_name": "Colorado hookless cactus",
                        "user_id": 1
                    }
                ],
                "user_id": 1
            }, 
            {
                "description": "Plants perennial, 30-70 cm tall. Stems glabrous and glaucus. Flowers in loose spike with 2 exserted stamens. Corolla deep blue to pinkish lavender.", 
                "id": 1, 
                "image_link": "http://www.cnhp.colostate.edu/rareplants/images/1/closeup3_19662.jpg", 
                "latin_name": "Penstemon harringtonii", 
                "name": "Harrington\u2019s beardtongue", 
                "plant_observations": [
                    {
                        "date": "September 04, 2019", 
                        "datetime": "Wed, 04 Sep 2019 16:28:00 GMT", 
                        "id": 11, 
                        "notes": "Came across this in collegiate mountains near Salida.", 
                        "plant_id": 1, 
                        "plant_image": "http://www.cnhp.colostate.edu/rareplants/images/1/closeup3_19662.jpg", 
                        "plant_name": "Harrington\u2019s beardtongue", 
                        "user_id": 1
                    }
                ], 
                "user_id": 1
            }, 
            {
                "description": "Stoloniferous perennial, stems 5-30 cm long. New fertile plants are produced wherever roots take hold.", 
                "id": 11, 
                "image_link": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_21230.jpg", 
                "latin_name": "Mimulus eastwoodiae", 
                "name": "Eastwood monkey-flower", 
                "plant_observations": [], 
                "user_id": 1
            }, 
        ], 
        "success": true
    }
    ```

#### GET /plants/\<id\>

* General:
  * Returns a plant using URL parameters specifying id of plant.
  * Does not require authorization.
* Sample request: 
    ```bash
    curl https://plant-survey-tool.herokuapp.com/api/plants/6
    ```
* Response:
    ```
    {
        "plant": {
            "description": "A squat, globular, spiny succulent. Each mature stem is 3-12 cm tall, 4-9 cm wide; the largest observed was 24 cm tall x 14 cm wide. However, during the driest part of the year the stem may shrink to below ground-level. Central spines are straight (hookless). The plants are inconspicuous except when in flower (April-May), when showy, fragrant, pink to magenta flowers appear at the top of the stem.", 
            "id": 6, 
            "image_link": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_16984.jpg", 
            "latin_name": "Sclerocactus glaucus", 
            "name": "Colorado hookless cactus", 
            "plant_observations": [
                {
                    "date": "June 21, 2018", 
                    "datetime": "Thu, 21 Jun 2018 11:11:00 GMT", 
                    "id": 7, 
                    "notes": "Seen near Glenwood Springs.", 
                    "plant_id": 6, 
                    "plant_image": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_16984.jpg", 
                    "plant_name": "Colorado hookless cactus", 
                    "user_id": 27
                }, 
                {
                    "date": "June 10, 2018", 
                    "datetime": "Sun, 10 Jun 2018 16:26:00 GMT", 
                    "id": 10, 
                    "notes": "Saw several on trail outside Grand Junction.", 
                    "plant_id": 6, 
                    "plant_image": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_16984.jpg", 
                    "plant_name": "Colorado hookless cactus", 
                    "user_id": 1
                }
            ], 
            "user_id": 1
        }, 
        "success": true
    }
    ```

#### POST /plants/new

* General:
  * Creates a new plant and adds it to the database.
  * Requires Admin account authorization.
    * Execute ```export ADMIN_ROLE_TOKEN=<active_admin_jwt>``` with active Admin JWT before request.
* Sample request:
    ```bash
    curl -d '{"name": "eastwood monkey-flower", "latinName": "Mimulus eastwoodiae", "description": "Stoloniferous perennial, stems 5-30 cm long. New fertile plants are produced wherever roots take hold.", "imageLink": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_21230.jpg"}' -H "Content-Type: application/json" -H "Authorization: Bearer $ADMIN_ROLE_TOKEN" -X POST https://plant-survey-tool.herokuapp.com/api/plants/new
    ```
* Response:
    ```
    {
        "plant": {
            "description": "Stoloniferous perennial, stems 5-30 cm long. New fertile plants are produced wherever roots take hold.", 
            "id": 14, 
            "image_link": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_21230.jpg", 
            "latin_name": "Mimulus eastwoodiae", 
            "name": "eastwood monkey-flower", 
            "plant_observations": [], 
            "user_id": 1
        }, 
        "success": true
    }
    ```

#### PATCH /plants/\<id\>/edit

* General:
    * Updates an existing plant using URL parameters specifying id of plant to be updated.
    * Request data object requires all key-value pairs shown below, but data will only update where value is not ```null```.
    * Requires Admin account authorization.
        * Execute ```export ADMIN_ROLE_TOKEN=<active_admin_jwt>``` with active Admin JWT before request.
* Sample request:
    ```bash
    curl -d '{"name": "Eastwood Monkey-Flower", "latinName": null, "description": null, "imageLink": null}' -H "Content-Type: application/json" -H "Authorization: Bearer $ADMIN_ROLE_TOKEN" -X PATCH https://plant-survey-tool.herokuapp.com/api/plants/14/edit
    ```
* Response:
    ```
    {
        "plant": {
            "description": "Stoloniferous perennial, stems 5-30 cm long. New fertile plants are produced wherever roots take hold.", 
            "id": 14, 
            "image_link": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_21230.jpg", 
            "latin_name": "Mimulus eastwoodiae", 
            "name": "Eastwood Monkey-Flower", 
            "plant_observations": [], 
            "user_id": 1
        }, 
        "success": true
    }
    ```

#### DELETE /plants/\<id\>/edit

* General:
    * Removes an existing plant from the database using URL parameters specifying id of plant to be deleted.
    * Requires Admin account authorization.
        * Execute ```export ADMIN_ROLE_TOKEN=<active_admin_jwt>``` with active Admin JWT before request.
* Sample request:
    ```bash
    curl -H "Authorization: Bearer $ADMIN_ROLE_TOKEN" -X DELETE https://plant-survey-tool.herokuapp.com/api/plants/14/edit
    ```
* Response:
    ```
    {
        "plant_id": 14, 
        "plant_name": "Eastwood Monkey-Flower", 
        "success": true
    }
    ```

#### GET /observations

* General:
  * Returns a list observations.
  * Does not require authorization.
* Sample request: 
    ```bash
    curl https://plant-survey-tool.herokuapp.com/api/observations
    ```
* Response:
    ```
    {
        "observations": [
            {
                "date": "July 12, 2019", 
                "datetime": "Fri, 12 Jul 2019 13:25:00 GMT", 
                "id": 9, 
                "notes": "Seen hiking in Rocky Mountain National Park.", 
                "plant_id": 1, 
                "plant_image": "http://www.cnhp.colostate.edu/rareplants/images/1/closeup3_19662.jpg", 
                "plant_name": "Harrington\u2019s beardtongue", 
                "user_id": 27
            }, 
            {
                "date": "June 21, 2018", 
                "datetime": "Thu, 21 Jun 2018 11:11:00 GMT", 
                "id": 7, 
                "notes": "Seen near Glenwood Springs.", 
                "plant_id": 6, 
                "plant_image": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_16984.jpg", 
                "plant_name": "Colorado hookless cactus", 
                "user_id": 27
            }, 
            {
                "date": "June 10, 2018", 
                "datetime": "Sun, 10 Jun 2018 16:26:00 GMT", 
                "id": 10, 
                "notes": "Saw several on trail outside Grand Junction.", 
                "plant_id": 6, 
                "plant_image": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_16984.jpg", 
                "plant_name": "Colorado hookless cactus", 
                "user_id": 1
            }, 
            {
                "date": "September 04, 2019", 
                "datetime": "Wed, 04 Sep 2019 16:28:00 GMT", 
                "id": 11, 
                "notes": "Came across this in collegiate mountains near Salida.", 
                "plant_id": 1, 
                "plant_image": "http://www.cnhp.colostate.edu/rareplants/images/1/closeup3_19662.jpg", 
                "plant_name": "Harrington\u2019s beardtongue", 
                "user_id": 1
            }
        ], 
        "success": true
    }

    ```


#### GET /observations/\<id\>

* General:
  * Returns an observation using URL parameters specifying id of observation.
  * Does not require authorization.
* Sample request: 
    ```bash
    curl https://plant-survey-tool.herokuapp.com/api/observations/9
    ```
* Response:
    ```
    {
        "observation": {
            "date": "July 12, 2019", 
            "datetime": "Fri, 12 Jul 2019 13:25:00 GMT", 
            "id": 9, 
            "notes": "Seen hiking in Rocky Mountain National Park.", 
            "plant_id": 1, 
            "plant_image": "http://www.cnhp.colostate.edu/rareplants/images/1/closeup3_19662.jpg", 
            "plant_name": "Harrington\u2019s beardtongue", 
            "user_id": 27
        }, 
        "success": true
    }
    ```


#### POST /observations/new

* General:
  * Creates a new observation and adds it to the database.
  * Requires Public or Admin account authorization.
    * Using active Public or Admin JWT before request, execute <br>
        ```export PUBLIC_ROLE_TOKEN=<active_public_jwt>``` <br>
        or <br>
        ```export ADMIN_ROLE_TOKEN=<active_admin_jwt>``` 
* Sample request:
    * note: value for "date" requires Python datetime.datetime object
    ```bash
    curl -d '{"date": "2020-01-16 08:14:02.649787", "plantID": 11, "notes": "seen in Boulder"}' -H "Content-Type: application/json" -H "Authorization: Bearer $PUBLIC_ROLE_TOKEN" -X POST https://plant-survey-tool.herokuapp.com/api/observations/new 
    ```
* Response:
    ```
    {
        "observation": {
            "date": "January 16, 2020", 
            "datetime": "Thu, 16 Jan 2020 08:14:02 GMT", 
            "id": 13, 
            "notes": "seen in Boulder", 
            "plant_id": 11, 
            "plant_image": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_21230.jpg", 
            "plant_name": "Eastwood monkey-flower", 
            "user_id": 27
        }, 
        "success": true
    }

    ```

#### PATCH /observations/\<id\>/edit

* General:
    * Updates an existing observation using URL parameters specifying id of observation to be updated.
    * Request data object requires all key-value pairs shown below, but data will only update where value is not ```null```.
    * Requires Public or Admin account authorization.
        * Using active Public or Admin JWT before request, execute <br>
            ```export PUBLIC_ROLE_TOKEN=<active_public_jwt>``` <br>
            or <br>
            ```export ADMIN_ROLE_TOKEN=<active_admin_jwt>``` 
* Sample request:
    ```bash
    curl -d '{"date": null, "notes": "seen in Boulder while hiking the Mesa Trail"}' -H "Content-Type: application/json" -H "Authorization: Bearer $PUBLIC_ROLE_TOKEN" -X PATCH https://plant-survey-tool.herokuapp.com/api/observations/13/edit
    ```
* Response:
    ```
    {
        "observation": {
            "date": "January 16, 2020", 
            "datetime": "Thu, 16 Jan 2020 08:14:02 GMT", 
            "id": 13, 
            "notes": "seen in Boulder while hiking the Mesa Trail", 
            "plant_id": 11, 
            "plant_image": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_21230.jpg", 
            "plant_name": "Eastwood monkey-flower", 
            "user_id": 27
        }, 
        "success": true
    }

    ```

#### DELETE /observations/\<id\>/edit

* General:
    * Removes an existing observation from the database using URL parameters specifying id of observation to be deleted.
    * Requires Public or Admin account authorization.
        * Using active Public or Admin JWT before request, execute <br>
            ```export PUBLIC_ROLE_TOKEN=<active_public_jwt>``` <br>
            or <br>
            ```export ADMIN_ROLE_TOKEN=<active_admin_jwt>```
* Sample request:
    ```bash
    curl -H "Authorization: Bearer $PUBLIC_ROLE_TOKEN" -X DELETE https://plant-survey-tool.herokuapp.com/api/observations/13/edit
    ```
* Response:
    ```
    {
        "observation_id": 13,
        "success": true
    }
    ```
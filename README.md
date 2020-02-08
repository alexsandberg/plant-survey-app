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
* Authentication: Most endpoints require either Public or Admin permissions. This version does not require authentication or API keys.

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
* 401 – authorization_header_missing
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
    curl https://plant-survey-tool.herokuapp.com/plants
    ```
* Response:
    ```
    {
        "plants": [
            {
                "description": "Plants perennial, 30-70 cm tall. Stems glabrous and glaucus. Flowers in loose spike with 2 exserted stamens.",
                "id": 3,
                "image_link": "http://www.cnhp.colostate.edu/rareplants/images/1/closeup3_19662.jpg",
                "latin_name": "Penstemon harringtonii",
                "name": "Harrington’s beardtongue",
                "plant_observations": [
                    {
                        "date": "Thu, 09 Jan 2020 16:55:24 GMT",
                        "id": 2,
                        "name": "Alex Sandberg",
                        "notes": "seen hiking in San Juan Mnts",
                        "plant_id": 3
                    }
                ]
            },
            {
                "description": "Flower petals 6-10 mm/0.2-0.4 in long, white with a yellow base.",
                "id": 4,
                "image_link": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_20366.jpg",
                "latin_name": "Physaria vicina",
                "name": "Good-neighbor bladderpod",
                "plant_observations": [
                    {
                        "date": "Sat, 09 Nov 2019 10:55:24 GMT",
                        "id": 3,
                        "name": "Alex Sandberg",
                        "notes": "seen hiking in RMNP",
                        "plant_id": 4
                    }
                ]
            },
            {
                "description": "Physaria pruinosa begins to flower by mid May with fruiting time depending on elevation.",
                "id": 5,
                "image_link": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_18927.jpg",
                "latin_name": "Physaria pruinosa",
                "name": "Pagosa bladderpod",
                "plant_observations": [
                    {
                        "date": "Sun, 21 Jul 2019 12:14:02 GMT",
                        "id": 4,
                        "name": "Alex Sandberg",
                        "notes": "seen in Gunnison",
                        "plant_id": 5
                    }
                ]
            },
        ], 
        "success": true
    }
    ```

#### POST /plants

* General:
  * Creates a new plant and adds it to the database.
  * Requires Admin account authorization.
    * Execute ```export ADMIN_ROLE_TOKEN=<active_admin_jwt>``` with active Admin JWT before request.
* Sample request:
    ```bash
    curl -d '{"name": "eastwood monkey-flower", "latinName": "Mimulus eastwoodiae", "description": "Stoloniferous perennial, stems 5-30 cm long. New fertile plants are produced wherever roots take hold.", "imageLink": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_21230.jpg"}' -H "Content-Type: application/json" -H "Authorization: Bearer $ADMIN_ROLE_TOKEN" -X POST https://plant-survey-tool.herokuapp.com/plants
    ```
* Response:
    ```
    {
        "plant": {
            "description": "Stoloniferous perennial, stems 5-30 cm long. New fertile plants are produced wherever roots take hold.", 
            "id": 15, 
            "image_link": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_21230.jpg", 
            "latin_name": "Mimulus eastwoodiae", 
            "name": "eastwood monkey-flower"
        }, 
        "success": true
    }
    ```

#### PATCH /plants/\<id\>

* General:
    * Updates an existing plant using URL parameters specifying id of plant to be updated.
    * Request data object requires all key-value pairs shown below, but data will only update where value is not ```null```.
    * Requires Admin account authorization.
        * Execute ```export ADMIN_ROLE_TOKEN=<active_admin_jwt>``` with active Admin JWT before request.
* Sample request:
    ```bash
    curl -d '{"name": "Eastwood Monkey-Flower", "latinName": null, "description": null, "imageLink": null}' -H "Content-Type: application/json" -H "Authorization: Bearer $ADMIN_ROLE_TOKEN" -X PATCH https://plant-survey-tool.herokuapp.com/plants/15
    ```
* Response:
    ```
    {
        "plant": {
            "description": "Stoloniferous perennial, stems 5-30 cm long. New fertile plants are produced wherever roots take hold.", 
            "id": 15, 
            "image_link": "https://cnhp.colostate.edu/rareplants/images/1/closeup1_21230.jpg", 
            "latin_name": "Mimulus eastwoodiae", 
            "name": "Eastwood Monkey-Flower"
        }, 
        "success": true
    }
    ```

#### DELETE /plants/\<id\>

* General:
    * Removes an existing plant from the database using URL parameters specifying id of plant to be deleted.
    * Requires Admin account authorization.
        * Execute ```export ADMIN_ROLE_TOKEN=<active_admin_jwt>``` with active Admin JWT before request.
* Sample request:
    ```bash
    curl -H "Authorization: Bearer $ADMIN_ROLE_TOKEN" -X DELETE https://plant-survey-tool.herokuapp.com/plants/15
    ```
* Response:
    ```
    {
        "plant_id": 15,
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
    curl https://plant-survey-tool.herokuapp.com/observations
    ```
* Response:
    ```
    {
        "observations": [
            {
                "date": "Thu, 09 Jan 2020 16:55:24 GMT",
                "id": 2,
                "name": "Alex Sandberg",
                "notes": "seen hiking in San Juan Mnts",
                "plant_id": 3
            },
            {
                "date": "Sat, 09 Nov 2019 10:55:24 GMT",
                "id": 3,
                "name": "Alex Sandberg",
                "notes": "seen hiking in RMNP",
                "plant_id": 4
            },
            {
                "date": "Sun, 21 Jul 2019 12:14:02 GMT",
                "id": 4,
                "name": "Alex Sandberg",
                "notes": "seen in Gunnison",
                "plant_id": 5
            }
        ],
        "success": true
    }
    ```

#### POST /observations

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
    curl -d '{"name": "Alex Sandberg", "date": "2020-01-16 08:14:02.649787", "plantID": 6, "notes": "seen in Boulder"}' -H "Content-Type: application/json" -H "Authorization: Bearer $PUBLIC_ROLE_TOKEN" -X POST https://plant-survey-tool.herokuapp.com/observations
    ```
* Response:
    ```
    {
        "observation": {
            "date": "Thu, 16 Jan 2020 08:14:02 GMT",
            "id": 5,
            "name": "Alex Sandberg",
            "notes": "seen in Boulder",
            "plant_id": 6
        },
        "success": true
    }
    ```

#### PATCH /observations/\<id\>

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
    curl -d '{"name": null, "date": null, "plantID": null, "notes": "seen in Boulder while hiking the Mesa Trail"}' -H "Content-Type: application/json" -H "Authorization: Bearer $PUBLIC_ROLE_TOKEN" -X PATCH https://plant-survey-tool.herokuapp.com/observations/5
    ```
* Response:
    ```
    {
        "observation": {
            "date": "Thu, 16 Jan 2020 08:14:02 GMT",
            "id": 5,
            "name": "Alex Sandberg",
            "notes": "seen in Boulder while hiking the Mesa Trail",
            "plant_id": 6
        },
        "success": true
    }
    ```

#### DELETE /observations/\<id\>

* General:
    * Removes an existing observation from the database using URL parameters specifying id of observation to be deleted.
    * Requires Public or Admin account authorization.
        * Using active Public or Admin JWT before request, execute <br>
            ```export PUBLIC_ROLE_TOKEN=<active_public_jwt>``` <br>
            or <br>
            ```export ADMIN_ROLE_TOKEN=<active_admin_jwt>```
* Sample request:
    ```bash
    curl -H "Authorization: Bearer $PUBLIC_ROLE_TOKEN" -X DELETE https://plant-survey-tool.herokuapp.com/observations/5
    ```
* Response:
    ```
    {
        "observation_id": 5,
        "observation_name": "Alex Sandberg",
        "success": true
    }
    ```
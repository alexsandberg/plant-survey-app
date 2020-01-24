import json
import os
from flask import request
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
ALGORITHMS = os.getenv('ALGORITHMS')
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE')
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CALLBACK_URL = os.getenv('AUTH0_CALLBACK_URL')

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """
    Obtains the Access Token from the Authorization Header
    """

    # get auth from header and verify auth exists
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    # split keyword and token
    parts = auth.split()

    # verify keyword is 'bearer', raise error if not
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    # auth header must have 2 parts
    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    # auth header must have 2 parts
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    # get token from parts and return
    token = parts[1]
    return token


def check_permissions(permission, payload):
    """
    Verifies user permissions
    """

    # verify permissions included in JWT
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    # verify user permissions from payload contain permission for given route
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 401)

    # return True if no AuthErrors raised
    return True


def verify_decode_jwt(token):
    '''
    Validates and decodes Auth0 JWTs
    '''

    # get public key from Auth0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # get header data from token
    unverified_header = jwt.get_unverified_header(token)

    # choose rsa key
    rsa_key = {}

    # validate token header contains kid
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        # if kid match, build rsa key
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            # validate the token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=AUTH0_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        # catch common errors

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)


def requires_auth(permission=''):
    '''
    Decorator fucntion used for adding authorization to endpoints
    '''
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # get token from header
            token = get_token_auth_header()

            # decode and validate token
            payload = verify_decode_jwt(token)

            # check user permissions
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator


def create_login_link():
    link = 'https://'
    link += AUTH0_DOMAIN
    link += '/authorize?'
    link += 'audience=' + AUTH0_AUDIENCE + '&'
    link += 'response_type=token&'
    link += 'client_id=' + AUTH0_CLIENT_ID + '&'
    link += 'redirect_uri=' + AUTH0_CALLBACK_URL
    return link

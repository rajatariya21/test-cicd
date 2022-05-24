from collections import defaultdict
from functools import wraps

from flask import request
from marshmallow import ValidationError

import app.main.common.constants as constants
from app.main.common.rest import RestManager


def check_api_validation(defined_schema):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # Get Request body from JSON
            request_data = request.json
            schema = defined_schema()
            try:
                # Validate request body against schema data types
                schema.load(request_data)
            except ValidationError as err:
                error_keys = []
                # Get schema keys
                for message_key in err.messages:
                    error_keys.append(message_key)

                # Return a nice message if validation fails
                rest_manager = RestManager()
                data = defaultdict(list)

                for every_error in err.messages:
                    if ["Unknown field."] != err.messages[every_error]:
                        if isinstance(err.messages[every_error], dict):
                            data["message"].append(
                                "Invalid {1} field in {0}".format(
                                    every_error,
                                    list(err.messages[every_error].keys())
                                    and list(err.messages[every_error].keys())[0],
                                )
                            )
                        if isinstance(err.messages[every_error], list):
                            data["message"].append(err.messages[every_error][0])
                return rest_manager.rest_response(
                    data=dict(data), status=constants.FAIL, status_code=400
                )
            return func(*args, **kwargs)

        return decorated_function

    return decorator

from dataclasses import asdict

from flask import request

import app.main.common.constants as constants
from app.main.common.ds import DataSource, get_request_json_as_dataclass
from app.main.common.rest import RestManager
from app.main.connector.airbyte.airbyte import AirbyteError, AirbyteIngestor





def create_destination():
    """Create a destination of ingestion.
    post:
    summary: Create a destination of ingestion service.
    requestBody:
        description: DataSource object that describes the destination to be created.
        required: true
    """
    rest_manager = RestManager()
    try:
        data = request.json
        destination = get_request_json_as_dataclass(DataSource, data)
        airbyte_ingeter = AirbyteIngestor()
        data = airbyte_ingeter.add_destination(destination)
        return rest_manager.rest_response(
            data=asdict(data), status=constants.SUCCESS, status_code=200
        )
    except (TypeError, KeyError, AirbyteError) as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=404
        )
    except Exception as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=500
        )


def delete_destination():
    """Delete the source of ingestion.
    post:
    summary: Delete a source of ingestion service.
    requestBody:
        description: DataSource object that describes the source to be deleted.
        required: true
    """
    rest_manager = RestManager()
    try:
        data = request.json
        destination = get_request_json_as_dataclass(DataSource, data)
        airbyte_ingeter = AirbyteIngestor()
        data = airbyte_ingeter.remove_destination(destination)
        return rest_manager.rest_response(
            data=constants.DESTINATION_DELETION_MESSAGE,
            status=constants.SUCCESS,
            status_code=200,
        )
    except (TypeError, KeyError, AirbyteError):
        return rest_manager.rest_response(
            data=None, status=constants.FAIL, status_code=404
        )
    except Exception:
        return rest_manager.rest_response(
            data=None, status=constants.FAIL, status_code=500
        )


def view_destination():
    """View the destination of ingestion.
    post:
    summary: View a destination of ingestion service.
    requestBody:
        description: DataSource object that describes the destination to be viewed.
        required: true
    """
    rest_manager = RestManager()
    try:
        data = request.json
        destination = get_request_json_as_dataclass(DataSource, data)
        airbyte_ingeter = AirbyteIngestor()
        data = airbyte_ingeter.get_destination(destination)
        return rest_manager.rest_response(
            data=asdict(data), status=constants.SUCCESS, status_code=200
        )
    except (TypeError, KeyError, AirbyteError):
        return rest_manager.rest_response(
            data=None, status=constants.FAIL, status_code=404
        )
    except Exception:
        return rest_manager.rest_response(
            data=None, status=constants.FAIL, status_code=500
        )


def update_destination():
    """Update a destination of ingestion.
    post:
    summary: Create a destination of ingestion service.
    requestBody:
        description: DataSource object that describes the destination to be updated.
        required: true
    """
    rest_manager = RestManager()
    try:
        data = request.json
        destination = get_request_json_as_dataclass(DataSource, data)
        airbyte_ingeter = AirbyteIngestor()
        data = airbyte_ingeter.update_destination(destination)
        return rest_manager.rest_response(
            data=asdict(data), status=constants.SUCCESS, status_code=200
        )
    except (TypeError, KeyError, AirbyteError):
        return rest_manager.rest_response(
            data=None, status=constants.FAIL, status_code=404
        )
    except Exception:
        return rest_manager.rest_response(
            data=None, status=constants.FAIL, status_code=500
        )

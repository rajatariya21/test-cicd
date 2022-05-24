from dataclasses import asdict

from flask import request
import json

import app.main.common.constants as constants
from app.main.common.ds import WeavDataSource, get_request_json_as_dataclass
from app.main.common.rest import RestManager
from app.main.connector.airbyte.airbyte import AirbyteError, AirbyteIngestor, ConfigException, ConnectionException, IntrospectionException,MongoException


def create_connector():
    """Create a connector for ingestion.
    post:
    summary: Create a connector for ingestion service.
    requestBody:
        description: DataSource object that
        describes the connector to be created.
        required: true
    """
    rest_manager = RestManager()
    try:
        data = request.json
        weav_data_source = get_request_json_as_dataclass(WeavDataSource, data)
        airbyte_ingeter = AirbyteIngestor()
        data = airbyte_ingeter.add_connector(weav_data_source)
        return rest_manager.rest_response(
            data=asdict(data), status=constants.SUCCESS, status_code=200
        )
    except AirbyteError as e:
        return rest_manager.rest_response(
            data={"connection_configurations":e.object,"message":str(e.message)}, status=constants.FAIL,
            status_code=e.status_code
        )
    except ConfigException as e:
        return rest_manager.rest_response(
            data={"connection_configurations":e.data,"message":str(e.message)}, status=constants.FAIL, status_code=412 # precondition failed status
        )
    except ConnectionException as e:
        return rest_manager.rest_response(
            data={"connection_configurations": e.data,"message":str(e.message)}, status=e.status, status_code=412 # precondition failed status
        )
    except MongoException as e:
        return rest_manager.rest_response(
            data={"message":str(e.message)}, status=constants.FAIL, status_code=503 # Mongodb unavailable status
        )
    except IntrospectionException as e:
        if e.status_code:
            error_code = e.status_code # introspection service status
        else:
            error_code = 503 # introspection service not available status
        return rest_manager.rest_response(
            data={"message":str(e.message)}, status=constants.FAIL, status_code=error_code # introspection service status
        )
    except (TypeError, KeyError, Exception) as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=500
        )


def update_connector():
    """Update a connector for ingestion.
    post:
    summary: Create a connector for ingestion service.
    requestBody:
        description: DataSource object
        that describes the connector to be updated.
        required: true
    """
    rest_manager = RestManager()
    try:
        data = request.json
        weav_data_source = get_request_json_as_dataclass(WeavDataSource, data)
        airbyte_ingeter = AirbyteIngestor()
        data = airbyte_ingeter.update_connector(weav_data_source)
        return rest_manager.rest_response(
            data=asdict(data), status=constants.SUCCESS, status_code=200
        )
    except AirbyteError as e:
        return rest_manager.rest_response(
            data=str(e.message), status=constants.FAIL,
            status_code=e.status_code
        )
    except MongoException as e:
        return rest_manager.rest_response(
            data={"message":str(e.message)}, status=constants.FAIL, status_code=503 # Mongodb unavailable status
        )
    except (TypeError, KeyError, Exception) as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=500
        )


def view_connector():
    """View the connector for ingestion.
    post:
    summary: View a connector for ingestion service.
    requestBody:
        description: DataSource object
        that describes the connector to be viewed.
        required: true
    """
    rest_manager = RestManager()
    try:
        data = request.json
        weav_data_source = get_request_json_as_dataclass(WeavDataSource, data)
        airbyte_ingeter = AirbyteIngestor()
        data = airbyte_ingeter.get_connector(weav_data_source)
        return rest_manager.rest_response(
            data=data, status=constants.SUCCESS, status_code=200
        )
    except (TypeError, KeyError, AirbyteError) as e:
        return rest_manager.rest_response(
            data=str(e.message), status=constants.FAIL,
            status_code=e.status_code
        )
    except Exception as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=500
        )


def delete_connector():
    """Delete the connector for ingestion.
    post:
    summary: Delete a connector for ingestion service.
    requestBody:
        description: DataSource object
        that describes the connector to be deleted.
        required: true
    """
    rest_manager = RestManager()
    try:
        data = request.json
        weav_data_source = get_request_json_as_dataclass(WeavDataSource, data)
        airbyte_ingeter = AirbyteIngestor()
        data = airbyte_ingeter.remove_connector(weav_data_source)
        return rest_manager.rest_response(
            data=constants.CONNECTOR_DELETED_SUCCESSFULLY + data.id,
            status=constants.SUCCESS,
            status_code=200,
        )
    except (TypeError, KeyError, AirbyteError) as e:
        return rest_manager.rest_response(
            data=str(e.message), status=constants.FAIL,
            status_code=e.status_code
        )
    except Exception as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=500
        )

def discover_schema():
    """Get stream data for the connector for ingestion.
    post:
    summary: Get stream data for the connector for ingestion.
    requestBody:
        description: DataSource object that describes the connector to be deleted.
        required: true
    """
    rest_manager = RestManager()
    try:
        data = request.json
        weav_data_source = get_request_json_as_dataclass(WeavDataSource, data)
        airbyte_ingeter = AirbyteIngestor()
        data = airbyte_ingeter.get_schema(weav_data_source)
        return rest_manager.rest_response(
            data=data,
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

def upload_file():
    """Ingesting local file using airbytes file connector

    Returns:
        Success message.
    """
    rest_manager = RestManager()
    try:
        data = request.files
        airbyte_ingeter = AirbyteIngestor()
        data = airbyte_ingeter.local_upload(data)
        return rest_manager.rest_response(
            data= data,
            status= constants.SUCCESS,
            status_code= 200,
        )
    except AirbyteError as e:
        return rest_manager.rest_response(
            data=e.message, status=constants.FAIL, status_code=e.status_code
        )
    except (TypeError, KeyError) as e:
        return rest_manager.rest_response(
            data=e, status=constants.FAIL, status_code=404
        )
    except Exception as e:
        return rest_manager.rest_response(
            data=e, status=constants.FAIL, status_code=500
        )
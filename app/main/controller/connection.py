from dataclasses import asdict

from flask import request
from marshmallow.fields import Constant

import app.main.common.constants as constants
from app.main.common.ds import (
    IngestionExecution,
    StatusData,
    WeavDataSource,
    get_request_json_as_dataclass,
)
from app.main.common.rest import RestManager
from app.main.connector.airbyte.airbyte import AirbyteError, AirbyteIngestor, DataserviceException





def create_connection():
    """Create a connection of ingestion service.
    ---
    post:
    summary: Create a connection of ingestion service.
    requestBody:
    description: IngestionRule object that describes the connection to be created.
    required: true"""
    rest_manager = RestManager()
    try:
        data = request.json
        weav_data_source = get_request_json_as_dataclass(WeavDataSource, data)
        airbyte_ingeter = AirbyteIngestor()
        data = airbyte_ingeter.add_connection(weav_data_source)
        return rest_manager.rest_response(
            data=data, status=constants.SUCCESS, status_code=200
        )
    except AirbyteError as e:
        return rest_manager.rest_response(
            data=str(e.message), status=constants.FAIL, status_code=404
        )
    except DataserviceException as e:
        return rest_manager.rest_response(
            data=str(e.message), status=constants.FAIL, status_code=e.status_code
        )
    except (TypeError, KeyError, Exception) as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=500
        )


def get_connection_status():
    """Create a get connection of ingestion service.
    ---
    post:
    summary: Create a get connection of ingestion service.
    requestBody:
    description: IngestionRule object that describes the connection ID.
    required: true"""
    rest_manager = RestManager()
    try:
        data = request.json
        ingestor = AirbyteIngestor()
        ingestion_execution = get_request_json_as_dataclass(IngestionExecution, data)
        ingestion_execution = ingestor.get_status_of_ingestion(ingestion_execution)
        data = ingestion_execution
        status_data = {
            constants.CONNECTOR_NAME: data.rule.source.name,
            constants.CONNECTOR_ID: data.rule.source.id,
            constants.STATUS: data.status,
            constants.IS_SYNCING: data.is_syncing,
            constants.CONNECTION_ID: data.id
        }
        if data.records_synced is not None:
            status_data[constants.REC_SYNC] = data.records_synced
        if data.dataset_id is not None:
            status_data["dataset_id"] = data.dataset_id
        status_data = get_request_json_as_dataclass(StatusData, status_data)
        return rest_manager.rest_response(
            data=asdict(status_data), status=constants.SUCCESS, status_code=200
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


def stop_connection():
    """Manually delete a connection of ingestion service.
    ---
    post:
    summary: Delete a connection to stop ingestion service.
    requestBody:
    description: IngestionRule object that describes the connection ID.
    required: true"""
    rest_manager = RestManager()
    try:
        data = request.json
        ingestor = AirbyteIngestor()
        ingestion_execution = get_request_json_as_dataclass(IngestionExecution, data)
        ingestion_execution = ingestor.delete_ingestion(ingestion_execution)
        data = ingestion_execution
        status_code = 200
        return rest_manager.rest_response(
            data=data, status=constants.SUCCESS, status_code=status_code
        )
    except (TypeError, KeyError, AirbyteError):
        return rest_manager.rest_response(
            data=None, status=constants.FAIL, status_code=404
        )
    except Exception:
        return rest_manager.rest_response(
            data=None, status=constants.FAIL, status_code=500
        )


def trigger_connection():
    """Manually sync a connection of ingestion service.
    ---
    post:
    summary: Trigger a connection of ingestion service.
    requestBody:
    description: IngestionRule object that describes the connection ID.
    required: true"""
    rest_manager = RestManager()
    try:
        data = request.json
        ingestor = AirbyteIngestor()
        ingestion_execution = get_request_json_as_dataclass(IngestionExecution, data)
        ingestion_execution = ingestor.trigger_ingestion(ingestion_execution)
        data = ingestion_execution
        return rest_manager.rest_response(
            data=data, status=constants.SUCCESS, status_code=200
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

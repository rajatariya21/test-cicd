from dataclasses import asdict

from flask import request

import app.main.common.constants as constants
from app.main.common.ds import (
    IngestionExecution,
    IngestionRule,
    get_request_json_as_dataclass,
)
from app.main.common.rest import RestManager
from app.main.connector.airbyte.airbyte import AirbyteError, AirbyteIngestor





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
        rule = get_request_json_as_dataclass(IngestionRule, data)
        ingestor = AirbyteIngestor()
        rule = ingestor.add_ingestion_rule(
            source=rule.source,
            destination=rule.destination,
            schema=rule.schema,
            schedule=rule.schedule,
            status=rule.status,
        )
        ingestion_execution = ingestor.ingestion_rule(rule, status=rule.status)
        ingestion_execution = ingestor.start_ingestion(ingestion_execution)
        data = ingestion_execution
        # logs = ingestion_execution.logs
        # errors = ingestion_execution.errors
        status_code = 200
        return rest_manager.rest_response(
            data=asdict(data), status=constants.SUCCESS, status_code=status_code
        )
    except (TypeError, KeyError, AirbyteError) as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=404
        )
    except Exception as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=500
        )


def delete_connection():
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
        data = None
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
    except (TypeError, KeyError, AirbyteError):
        return rest_manager.rest_response(
            data=None, status=constants.FAIL, status_code=404
        )
    except Exception:
        return rest_manager.rest_response(
            data=None, status=constants.FAIL, status_code=500
        )


def get_connection():
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


def list_connection():
    """Get all connection in a workspace.
    ---
    post:
    summary: Get all connection in a workspace.
    requestBody:
    description: IngestionRule object that describes the workspaceId ID.
    required: true"""
    rest_manager = RestManager()
    try:
        data = request.json
        ingestor = AirbyteIngestor()
        ingestion_execution = get_request_json_as_dataclass(IngestionExecution, data)
        ingestion_execution = ingestor.list_ingestion(ingestion_execution)
        data = ingestion_execution
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

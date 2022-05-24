# from dataclasses import asdict

from flask import request

import app.main.common.constants as constants
from app.main.common.ds import (
    WeavDataSource,
    BackendService,
    StreamPreview,
    get_request_json_as_dataclass
    )
from app.main.common.rest import RestManager
from app.main.connector.airbyte.airbyte import AirbyteError, AirbyteIngestor
from flask import current_app


def getall_list():
    """Returns All sources defination lists from airbyte.
    post:
    summary: returns All sources defination lists from airbyte.
    requestBody: None.
    """
    rest_manager = RestManager()
    try:
        airbyte_ingeter = AirbyteIngestor()
        ret_data = airbyte_ingeter.getall_list()
        return rest_manager.rest_response(
            data=ret_data, status=constants.SUCCESS, status_code=200
        )
    except (TypeError, KeyError, AirbyteError) as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=404
        )
    except Exception as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=500
        )


def get_display_list():
    """Returns Configurations for selected sources from airbyte.
    post:
    summary: Returns Configurations for selected sources from airbyte.
    requestBody: Source defination ID.
    """
    rest_manager = RestManager()
    try:
        data = request.json
        airbyte_ingeter = AirbyteIngestor()
        ret_data = airbyte_ingeter.get_display_list(data)
        return rest_manager.rest_response(
            data=ret_data, status=constants.SUCCESS, status_code=200
        )
    except AirbyteError as e:
        return rest_manager.rest_response(
            data=str(e.message), status=constants.FAIL, status_code=e.status_code
        )
    except (TypeError, KeyError) as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=404
        )
    except Exception as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=500
        )


def getuser_conn_list():
    """Returns All sources created by user.
    post:
    summary: Returns All sources created by user.
    requestBody: UserId.
    """
    rest_manager = RestManager()
    try:
        data = request.json
        data = get_request_json_as_dataclass(WeavDataSource, data)
        airbyte_ingeter = AirbyteIngestor()
        ret_data = airbyte_ingeter.getuser_conn_list(data)
        return rest_manager.rest_response(
            data=ret_data, status=constants.SUCCESS, status_code=200
        )
    except (TypeError, KeyError) as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=404
        )
    except Exception as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=500
        )


def get_stepper_ui():
    """Returns Stepper ui config for Airbyte add dataset flow

    requestBody: Stepper ui config list
    """
    rest_manager = RestManager()
    try:
        data = request.json
        data = get_request_json_as_dataclass(BackendService, data)
        airbyte_ingeter = AirbyteIngestor()
        ret_data = airbyte_ingeter.get_stepper_ui(data)
        return rest_manager.rest_response(
            data=ret_data, status=constants.SUCCESS, status_code=200
        )
    except (TypeError, KeyError) as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=404
        )
    except Exception as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=500
        )

def get_stream_preview():
    """Returns preview for selected stream for current dataset

    requestBody: Stream name,connection_id
    """
    rest_manager = RestManager()
    try:
        data = request.json
        data = get_request_json_as_dataclass(StreamPreview, data)
        airbyte_ingeter = AirbyteIngestor()
        ret_data = airbyte_ingeter.get_stream_preview(data)
        return ret_data
        # return rest_manager.rest_response(
        #     data=ret_data, status=constants.SUCCESS, status_code=200
        # )
    except (TypeError, KeyError, FileNotFoundError) as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=404
        )
    except Exception as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=500
        )

def sync_webhook():
    """Returns All sources defination lists from airbyte.
    post:
    summary: returns All sources defination lists from airbyte.
    requestBody: None.
    """
    rest_manager = RestManager()
    try:
        data = request.json
        if constants.WEBHOOK_TEST_CALL in data["text"]:
            current_app.logger.info("Airbyte Webhook test call")
            current_app.logger.info(data["text"])
            ret_data = data
        else:
            # print(data["text"].split('\n')[3].split("/")[-1])
            airbyte_ingeter = AirbyteIngestor()
            ret_data = airbyte_ingeter.webhook_sync(data)
        return rest_manager.rest_response(
            data=ret_data, status=constants.SUCCESS, status_code=200
        )
    except (TypeError, KeyError, AirbyteError) as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=404
        )
    except Exception as e:
        return rest_manager.rest_response(
            data=str(e), status=constants.FAIL, status_code=500
        )
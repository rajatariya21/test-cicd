from dataclasses import asdict

from flask import request

import app.main.common.constants as constants
from app.main.common.ds import WorkspaceData, get_request_json_as_dataclass
from app.main.common.rest import RestManager
from app.main.connector.airbyte.airbyte import AirbyteError, AirbyteIngestor





def create_workspace():
    """Create a workspace for ingestion.
    post:
    summary: Create a workspace for ingestion service.
    requestBody:
        description: WorkspaceData object that describes the workspace to be created.
        required: true
    """
    rest_manager = RestManager()
    try:
        data = request.json
        weav_data_source = get_request_json_as_dataclass(WorkspaceData, data)
        airbyte_ingeter = AirbyteIngestor()
        ret_data = airbyte_ingeter.create_workspace(
            name=weav_data_source.name,
            email=weav_data_source.email,
            anonymous_data_collection=weav_data_source.anonymous_data_collection,
            news=weav_data_source.news,
            security_updates=weav_data_source.security_updates,
            notifications=weav_data_source.notifications,
        )
        data_dict = {}
        # redefining returned dictionary with only keys which have any values
        # i.e. removing items with empty values.
        for k, v in ret_data.items():
            if v:
                data_dict[k] = v
        data = get_request_json_as_dataclass(WorkspaceData, data_dict)
        data.workspace_id = ret_data[constants.AIRBYTE_WORKSPACE_ID]
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

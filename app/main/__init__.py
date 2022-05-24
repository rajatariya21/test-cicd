from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from werkzeug.utils import send_from_directory
import app.main.common.constants as constants
from os import environ
import json
import requests
from app.main.connector.airbyte.airbyte import AirbyteIngestor

from .routes.connection import routes_connection_api
from .routes.connections import routes_connections_api
from .routes.connector import routes_connector_api
from .routes.destinations import routes_destinations_api
from .routes.sources import routes_sources_api
from .routes.workspace import routes_workspace_api
from .routes.connectors import routes_connectors_api


def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.register_blueprint(routes_sources_api, url_prefix="/api/v1/sources")
    app.register_blueprint(routes_destinations_api, url_prefix="/api/v1/destinations")
    app.register_blueprint(routes_connections_api, url_prefix="/api/v1/connections")
    app.register_blueprint(routes_connector_api, url_prefix="/api/v1/connector")
    app.register_blueprint(routes_connection_api, url_prefix="/api/v1/connection")
    app.register_blueprint(routes_workspace_api, url_prefix="/api/v1/workspace")
    app.register_blueprint(routes_connectors_api, url_prefix="/api/v1/connectors")

    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)

    # ## swagger specific ###
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.yml'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Weav.AI Ingestion Service"
        }
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
    # ## end swagger specific ###

    @app.before_first_request
    def before_first_request():
        app.logger.info("before_first_request: Creating custom destination defination")
        airbyte_web_host = environ.get(constants.AIRBYTE_WEB_HOST,constants.AB_LOCALHOST)
        url = constants.AB_DEST_DEF_CREATE_URL.format(airbyte_web_host)
        payload = json.dumps(
                {
                    constants.AIRBYTE_NAME: constants.AB_CUST_DEST,
                    constants.AB_DOC_URL: constants.AIRBYTE_DOC_URL,
                    constants.AIRBYTE_DOCKER_TAG: constants.AIRBYTE_DEV,
                    constants.AB_DOC_REPO: constants.WEAV_DEST_CUSTOM_PYTHON,
                }
            )
        headers = {constants.AB_CONTENT_TYPE: constants.AB_APP_JSON}
        requests.request(
                constants.REQUEST_POST, url, headers=headers, data=payload
            )
    
    @app.before_first_request
    def airbyte_webhook_update():
        app.logger.info("before_first_request: updating ab webhook config")
        airbyte_web_host = environ.get(constants.AIRBYTE_WEB_HOST,constants.AB_LOCALHOST)
        url = constants.AB_WEBHOOK_URL.format(airbyte_web_host)
        airbyte_ingester = AirbyteIngestor()
        workspace_id = airbyte_ingester.get_airbyte_workspace_id()
        payload = json.dumps(
            {
            "workspaceId":workspace_id,
            "initialSetupComplete":True,
            "displaySetupWizard":True,
            "anonymousDataCollection":False,
            "news":False,
            "securityUpdates":True,
            "notifications":
            [
                {
                    "notificationType":"slack",
                    "sendOnSuccess":True,
                    "sendOnFailure":True,
                    "slackConfiguration":
                        {
                            "webhook":"http://172.55.0.111:7002/api/v1/connectors/sync_webhook"
                        }
                }
            ]
        }
        )
        headers = {constants.AB_CONTENT_TYPE: constants.AB_APP_JSON}
        requests.request(
                constants.REQUEST_POST, url, headers=headers, data=payload
            )

    return app

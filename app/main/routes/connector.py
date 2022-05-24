from flask import Blueprint

from app.main.controller import connector as connector_controller
from app.main.middleware.api_validator import check_api_validation
from app.main.route_models.connector import (
    CreateConnector,
    DeleteConnector,
    UpdateConnector,
    ViewConnector
)

routes_connector_api = Blueprint("routes_connector_api", __name__)


@routes_connector_api.route("/configure", methods=["POST"])
@check_api_validation(CreateConnector)
def redirect_create_connector():
    return connector_controller.create_connector()


@routes_connector_api.route("/update", methods=["POST"])
@check_api_validation(UpdateConnector)
def redirect_update_connector():
    return connector_controller.update_connector()


@routes_connector_api.route("/get", methods=["POST"])
@check_api_validation(ViewConnector)
def redirect_view_connector():
    return connector_controller.view_connector()


@routes_connector_api.route("/delete", methods=["DELETE"])
@check_api_validation(DeleteConnector)
def redirect_delete_connector():
    return connector_controller.delete_connector()


@routes_connector_api.route("/discover_schema", methods=["POST"])
@check_api_validation(ViewConnector)
def redirect_discover_schema_connector():
    return connector_controller.discover_schema()


@routes_connector_api.route("/local_upload", methods=["POST"])
def redirect_upload_file_connector():
    return connector_controller.upload_file()
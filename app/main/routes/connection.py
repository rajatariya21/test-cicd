from flask import Blueprint

from app.main.controller import connection as connection_controller
from app.main.middleware.api_validator import check_api_validation
from app.main.route_models.connection import (
    CreateConnection,
    DeleteConnection,
    InspectConnection,
    TriggerConnection,
)

routes_connection_api = Blueprint("routes_connection_api", __name__)


@routes_connection_api.route("/create", methods=["POST"])
@check_api_validation(CreateConnection)
def redirect_create_connection():
    return connection_controller.create_connection()


@routes_connection_api.route("/status", methods=["POST"])
@check_api_validation(InspectConnection)
def redirect_get_connection_status():
    return connection_controller.get_connection_status()


@routes_connection_api.route("/trigger", methods=["POST"])
@check_api_validation(TriggerConnection)
def redirect_trigger_connection():
    return connection_controller.trigger_connection()


@routes_connection_api.route("/delete", methods=["DELETE"])
@check_api_validation(DeleteConnection)
def redirect_stop_connection():
    return connection_controller.stop_connection()

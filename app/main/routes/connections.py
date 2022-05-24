from flask import Blueprint

from app.main.controller import connections as connections_controller
from app.main.middleware.api_validator import check_api_validation
from app.main.route_models.connections import (
    CreateConnection,
    DeleteConnection,
    InspectConnection,
    ListConnection,
    TriggerConnection,
)

routes_connections_api = Blueprint("routes_connections_api", __name__)

# Connections


@routes_connections_api.route("/create", methods=["POST"])
@check_api_validation(CreateConnection)
def redirect_create_connection():
    return connections_controller.create_connection()


@routes_connections_api.route("/read", methods=["POST"])
@check_api_validation(InspectConnection)
def redirect_view_connection():
    return connections_controller.get_connection()


@routes_connections_api.route("/delete", methods=["POST"])
@check_api_validation(DeleteConnection)
def redirect_delete_connection():
    return connections_controller.delete_connection()


@routes_connections_api.route("/trigger", methods=["POST"])
@check_api_validation(TriggerConnection)
def redirect_update_connection():
    return connections_controller.trigger_connection()


@routes_connections_api.route("/list", methods=["POST"])
@check_api_validation(ListConnection)
def redirect_list_connection():
    return connections_controller.list_connection()

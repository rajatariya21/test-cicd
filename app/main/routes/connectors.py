from flask import Blueprint

from app.main.controller import connectors as connectors_controller
from app.main.middleware.api_validator import check_api_validation
from app.main.route_models.connectors import (
    Get_display_list,
    Getuser_conn_list,
    Get_stepper_object,
    Get_stream_preview
    )

routes_connectors_api = Blueprint("routes_connectors_api", __name__)


@routes_connectors_api.route("/get_all", methods=["GET", "POST"])
# @check_api_validation()
def redirect_getall():
    return connectors_controller.getall_list()


@routes_connectors_api.route("/get_display_list", methods=["POST"])
@check_api_validation(Get_display_list)
def redirect_get_display_list():
    return connectors_controller.get_display_list()


@routes_connectors_api.route("/get", methods=["POST"])
@check_api_validation(Getuser_conn_list)
def redirect_getuser_conn_all():
    return connectors_controller.getuser_conn_list()


@routes_connectors_api.route("/get_stepper_ui", methods=["GET", "POST"])
@check_api_validation(Get_stepper_object)
def redirect_get_stepper_ui():
    return connectors_controller.get_stepper_ui()


@routes_connectors_api.route("/get_stream_preview", methods=["POST"])
@check_api_validation(Get_stream_preview)
def redirect_get_stream_preview():
    return connectors_controller.get_stream_preview()

@routes_connectors_api.route("/sync_webhook", methods=["GET", "POST"])
# @check_api_validation(Get_stream_preview)
def redirect_sync_webhook():
    return connectors_controller.sync_webhook()
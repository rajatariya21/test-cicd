from flask import Blueprint

from app.main.controller import destinations as destinations_controller
from app.main.middleware.api_validator import check_api_validation
from app.main.route_models.destinations import (
    CreateDestination,
    DeleteDestination,
    UpdateDestination,
    ViewDestination,
)

# from middleware import api_validation

routes_destinations_api = Blueprint("routes_destinations_api", __name__)
# Destination


@routes_destinations_api.route("/create", methods=["POST"])
@check_api_validation(CreateDestination)
def redirect_create_destination():
    return destinations_controller.create_destination()


@routes_destinations_api.route("/read", methods=["POST"])
@check_api_validation(ViewDestination)
def redirect_view_destination():
    return destinations_controller.view_destination()


@routes_destinations_api.route("/delete", methods=["POST"])
@check_api_validation(DeleteDestination)
def redirect_delete_destination():
    return destinations_controller.delete_destination()


@routes_destinations_api.route("/update", methods=["POST"])
@check_api_validation(UpdateDestination)
def redirect_update_destination():
    return destinations_controller.update_destination()

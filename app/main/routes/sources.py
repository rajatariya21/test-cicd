from flask import Blueprint

from app.main.controller import sources as sources_controller
from app.main.middleware.api_validator import check_api_validation
from app.main.route_models.sources import (
    CreateSource,
    DeleteSource,
    UpdateSource,
    ViewSource,
)

routes_sources_api = Blueprint("routes_sources_api", __name__)


@routes_sources_api.route("/create", methods=["POST"])
@check_api_validation(CreateSource)
def redirect_create_source():
    return sources_controller.create_source()


@routes_sources_api.route("/read", methods=["POST"])
@check_api_validation(ViewSource)
def redirect_view_source():
    return sources_controller.view_source()


@routes_sources_api.route("/delete", methods=["POST"])
@check_api_validation(DeleteSource)
def redirect_delete_source():
    return sources_controller.delete_source()


@routes_sources_api.route("/update", methods=["POST"])
@check_api_validation(UpdateSource)
def redirect_update_source():
    return sources_controller.update_source()

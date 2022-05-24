from flask import Blueprint

from app.main.controller import workspace as workspace_controller
from app.main.middleware.api_validator import check_api_validation
from app.main.route_models.workspace import CreateWorkspace

routes_workspace_api = Blueprint("routes_workspace_api", __name__)


@routes_workspace_api.route("/create", methods=["POST"])
@check_api_validation(CreateWorkspace)
def redirect_create_workspace():
    return workspace_controller.create_workspace()

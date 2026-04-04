from flask import Blueprint

from ..middleware.auth_middleware import inject_current_user
from ..services.dashboard_service import build_dashboard_payload
from ..utils.response import success_response


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/v1/dashboard")


@dashboard_bp.get("")
@inject_current_user
def get_dashboard(current_user):
    return success_response(
        data=build_dashboard_payload(current_user),
        message="Data dashboard berhasil diambil.",
    )

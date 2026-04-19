from flask import Blueprint, jsonify
from ..models.sekolah import SekolahInfo

school_bp = Blueprint('school', __name__, url_prefix='/api/v1/school')

@school_bp.get('/')
def get_school():
    """Return school info together with operational summary."""
    info = SekolahInfo.query.first()
    if not info:
        return jsonify({"success": False, "message": "School info not found."}), 404
    return jsonify({
        "success": True,
        "data": info.to_dict(),
        "summary": info.summary(),
    })

from flask import Blueprint, request
from structure import structure


users_blueprint = Blueprint("users_v1", __name__)


@users_blueprint.route("/", methods=["POST"])
def create():
    return structure.register_handler.handle(request)

from flask import Blueprint, request
from structure import structure


auth_blueprint = Blueprint("auth_v1", __name__)


@auth_blueprint.route("/login", methods=["POST"])
def login():
    return structure.login_handler.handle(request)


@auth_blueprint.route("/refresh", methods=["POST"])
def refresh():
    return structure.refresh_handler.handle(request)


@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    return structure.logout_handler.handle(request)

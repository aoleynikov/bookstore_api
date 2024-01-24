from flask import Blueprint, request
from structure import structure

inventory_blueprint = Blueprint("inventory", __name__)


@inventory_blueprint.route("/", methods=["GET"])
def get_inventory_list():
    return structure.get_inventory_list_handler.handle(request)

@inventory_blueprint.route("/", methods=["POST"])
def create_inventory_item():
    return structure.create_inventory_item_handler.handle(request)

@inventory_blueprint.route("/<item_id>", methods=["PUT"])
def update_inventory_item(item_id):
    return structure.update_inventory_item_handler.handle(request, item_id=item_id)


@inventory_blueprint.route("/<item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    return structure.delete_inventory_item_handler.handle(request, item_id=item_id)

@inventory_blueprint.route("/<item_id>/alert", methods=["PUT"])
def create_inventory_item_alert(item_id):
    return structure.create_inventory_alert_handler.handle(request, item_id=item_id)
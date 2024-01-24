from flask import Flask

from blueprints.v1.auth_blueprint import auth_blueprint
from blueprints.v1.users_blueprint import users_blueprint
from blueprints.v1.inventory_blueprint import inventory_blueprint

from flask_swagger_ui import get_swaggerui_blueprint

import os

SWAGGER_URL="/swagger"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    "/swagger_definition",
)

app = Flask(__name__)

@app.route("/swagger_definition")
def swagger_definition():
    with open(os.path.join(os.path.dirname(__file__), "swagger/definitions.json")) as f:
        return f.read()

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(inventory_blueprint, url_prefix="/inventory")

if __name__ == "__main__":
    app.run(debug=True)

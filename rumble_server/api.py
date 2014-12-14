import json
import os
from flask import Flask, request
from flask_restful import Api
from rumble_server.resources import User


def create_app():
    app = Flask(__name__)
    api = Api(app)

    resource_map = (
        (User, '/register'),
    )

    for resource, route in resource_map:
        api.add_resource(resource, route)

    return app


if __name__ == "__main__":
    print("If you run locally, browse to localhost:5000")
    host = '0.0.0.0'
    port = int(os.environ.get("PORT", 5000))
    app = create_app()
    #app.run(debug=opts.debug, port=opts.port, host=opts.host)
    app.run(host=host, port=port)

import argparse
import os
from flask import Flask
from flask_restful import Api
from resources import User, Users, ActiveUser, RoomMember, RoomMembers, Room, Rooms, Message, Messages
from flask_cors import CORS

import server


def main():
    port = 5555

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db-path')
    db_path = parser.parse_args().db_path

    print("If you run locally, browse to localhost:{}".format(port))
    host = '0.0.0.0'
    port = int(os.environ.get("PORT", port))

    # app.run(debug=opts.debug, port=opts.port, host=opts.host)
    the_app = create_app(db_path)
    the_app.run(host=host, port=port)

def create_app(db_path):
    if db_path is not None:
        server.db_path = db_path
    app = Flask(__name__)
    CORS(app)
    api = Api(app)

    resource_map = (
        (User, '/user'),
        (Users, '/users'),
        (ActiveUser, '/active_user'),
        (RoomMember, '/room_member/<name>'),
        (RoomMembers, '/room_members/<name>'),
        (Room, '/room/<name>'),
        (Rooms, '/rooms'),
        (Message, '/message/<name>'),
        (Messages, '/messages/<name>/<start>/<end>')
    )

    for resource, route in resource_map:
        api.add_resource(resource, route)

    return app


if __name__ == "__main__":
    main()

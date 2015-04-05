import os
from flask import Flask
from flask_restful import Api
from resources import User, Users, ActiveUser, RoomMember, RoomMembers, Room, Rooms, Message, Messages


def create_app():
    app = Flask(__name__)
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

the_app = create_app()

if __name__ == "__main__":
    port = 5555
    print("If you run locally, browse to localhost:{}".format(port))
    host = '0.0.0.0'
    port = int(os.environ.get("PORT", port))
    #app.run(debug=opts.debug, port=opts.port, host=opts.host)
    the_app.run(host=host, port=port)

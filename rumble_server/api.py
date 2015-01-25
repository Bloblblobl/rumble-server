import os
from flask import Flask
from flask_restful import Api
from resources import User, ActiveUser, RoomMember, RoomMembers, Room, Rooms, Message, Messages


def create_app():
    app = Flask(__name__)
    api = Api(app)

    resource_map = (
        (User, '/user'),
        (ActiveUser, '/active_user'),
        (RoomMember, '/room_member'),
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
    print("If you run locally, browse to localhost:5000")
    host = '0.0.0.0'
    port = int(os.environ.get("PORT", 5000))
    #app.run(debug=opts.debug, port=opts.port, host=opts.host)
    the_app.run(host=host, port=port)

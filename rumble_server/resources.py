from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from server import get_instance


class User(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('handle', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        server = get_instance()
        server.register(**args)
        return dict(result='OK')


class LoggedInUser(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        server = get_instance()
        user_id = server.login(**args)
        return dict(user_id=user_id)

class RoomMember(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument('user_id', type=str, required=True)
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args()
        server = get_instance()
        server.join_room(**args)

    def delete(self):
        parser = RequestParser()
        parser.add_argument('user_id', type=str, required=True)
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args()
        server = get_instance()
        server.leave_room(**args)

class RoomMembers(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument('user_id', type=str, required=True)
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args()
        server = get_instance()
        return dict(result=server.get_room_members(**args))


class Room(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument('user_id', type=str, required=True)
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args()
        server = get_instance()
        server.create_room(**args)

    def delete(self):
        parser = RequestParser()
        parser.add_argument('user_id', type=str, required=True)
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args()
        server = get_instance()
        server.destroy_room(**args)

class Rooms(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument('user_id', type=str, required=True)
        args = parser.parse_args()
        server = get_instance()
        return dict(result=server.get_rooms(**args))





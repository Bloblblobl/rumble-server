from flask import request
from flask_restful import Resource, abort
from flask_restful.reqparse import RequestParser
from server import get_instance


class User(Resource):
    def post(self):
        try:
            parser = RequestParser()
            parser.add_argument('username', type=str, required=True)
            parser.add_argument('handle', type=str, required=True)
            parser.add_argument('password', type=str, required=True)
            args = parser.parse_args()
            server = get_instance()
            server.register(**args)
            return dict(result='OK')
        except Exception as e:
            raise

class Users(Resource):
    def get(self):
        if 'Authorization' not in request.headers:
            abort(401, message='Unauthorized user')
        user_auth = request.headers['Authorization']

        server = get_instance()
        return dict(result=server.get_users(user_auth=user_auth))


class ActiveUser(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        server = get_instance()
        user_auth = server.login(**args)
        return dict(user_auth=user_auth)

    def delete(self):
        try:
            user_auth = request.headers['Authorization']
        except Exception as e:
            raise
        server = get_instance()
        server.logout(user_auth)
        return dict(result='OK')


class RoomMember(Resource):
    def post(self, name):
        user_auth = request.headers['Authorization']
        server = get_instance()
        server.join_room(user_auth=user_auth, name=name)
        return dict(result='OK')

    def delete(self, name):
        user_auth = request.headers['Authorization']
        server = get_instance()
        server.leave_room(user_auth=user_auth, name=name)
        return dict(result='OK')


class RoomMembers(Resource):
    def get(self, name):
        user_auth = request.headers['Authorization']
        server = get_instance()
        result = server.get_room_members(user_auth=user_auth, name=name)
        return dict(result=result)


class Room(Resource):
    def post(self, name):
        user_auth = request.headers['Authorization']
        server = get_instance()
        server.create_room(user_auth=user_auth, name=name)
        return dict(result='OK')

    def delete(self, name):
        user_auth = request.headers['Authorization']
        server = get_instance()
        server.destroy_room(user_auth=user_auth, name=name)
        return dict(result='OK')


class Rooms(Resource):
    def get(self):
        user_auth = request.headers['Authorization']
        server = get_instance()
        return dict(result=server.get_rooms(user_auth=user_auth))


class Message(Resource):
    def post(self, name):
        user_auth = request.headers['Authorization']
        parser = RequestParser()
        parser.add_argument('message', type=str, required=True)
        message = parser.parse_args()['message']
        server = get_instance()
        server.handle_message(user_auth, name, message)
        return dict(result='OK')


class Messages(Resource):
    def get(self, name, start, end):
        user_auth = request.headers['Authorization']
        server = get_instance()
        result = server.get_messages(user_auth, name, start, end)
        result = [(r[0].isoformat(), r[1], r[2]) for r in result]
        return dict(result=result)






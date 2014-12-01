import json
import os
from flask import Flask, request
from flask_restful import Api
from server import Server

rumble = None

def create_app():
    global rumble
    rumble = Server()
    app = Flask(__name__)
    api = Api(app)
    return app


# @app.route('/')
# def hello_flask():
#     return 'Hello Flask!'
#
#
# @app.route('/register', methods=['POST'])
# def register():
#     username = request.form['username']
#     password = request.form['password']
#     handle = request.form['handle']
#     server.register(username, password, handle)
#     return json.dumps(result='OK')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != app.config['USERNAME']:
#             error = 'Invalid username'
#         elif request.form['password'] != app.config['PASSWORD']:
#             error = 'Invalid password'
#         else:
#             session['logged_in'] = True
#             flash('You were logged in')
#             return redirect(url_for('show_entries'))
#     return render_template('login.html', error=error)

    from rumble_server.resources import User

    resource_map = (
        (User, '/register'),
    )

    for resource, route in resource_map:
        api.add_resource(resource, route)



if __name__ == "__main__":
    print("If you run locally, browse to localhost:5000")
    #host = '0.0.0.0'
    host = 'localhost'
    port = int(os.environ.get("PORT", 5000))
    app = create_app()
    #app.run(debug=opts.debug, port=opts.port, host=opts.host)
    app.run(host=host, port=port)
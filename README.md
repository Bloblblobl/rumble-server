Rumble-Server
=============
*Python 2*-based Chat Server
Will Use **Flask-Restful** and **SQLite Database**

[Project Map](https://docs.google.com/document/d/1pwb8R2YV4yL0URVyQtsfOuqbDk4sDiX6KIOshKuWdHQ)

1. Login to PythonAnywhere
2. Go to Bash Console
3. Execute the Following Commands:
    cd Rumble-Server/
    git pull --rebase
4. Reload the App from the Dashboard

## Local Setup
- Download [sqlite3](https://www.sqlite.org/download.html) and add to path
- Create SQLite Database called 'rumble.db' in the rumble_server directory
- Execute the 'rumble_schema.sql'
- pipenv --two
- pipenv install    
- pipenv run python api.py

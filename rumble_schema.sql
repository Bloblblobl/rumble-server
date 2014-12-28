BEGIN TRANSACTION

CREATE TABLE room(
id INTEGER PRIMARY KEY,
name TEXT);

CREATE TABLE user(
id INTEGER PRIMARY KEY,
name TEXT,
password TEXT,
handle TEXT);

CREATE TABLE membership(
id INTEGER PRIMARY KEY,
user_id references user(id),
room_id references room(id));

CREATE TABLE message(
id INTEGER PRIMARY KEY,
user_id TEXT,
timestamp TEXT,
message TEXT);

END TRANSACTION
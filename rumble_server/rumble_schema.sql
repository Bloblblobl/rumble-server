BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS room(
id INTEGER PRIMARY KEY,
name TEXT);

CREATE TABLE IF NOT EXISTS user(
id INTEGER PRIMARY KEY,
name TEXT,
password TEXT,
handle TEXT);

CREATE TABLE IF NOT EXISTS membership(
id INTEGER PRIMARY KEY,
user_id references user(id),
room_id references room(id));

CREATE TABLE IF NOT EXISTS message(
id INTEGER PRIMARY KEY,
room_id references room(id),
user_id references user(id),
timestamp TEXT,
message TEXT);

INSERT INTO room (name) VALUES ('room0');

END TRANSACTION;
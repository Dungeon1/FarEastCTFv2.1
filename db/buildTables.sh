#!/bin/bash

sqlite3 fectf.db 'CREATE TABLE categories ( id INTEGER PRIMARY KEY, name TEXT );'
sqlite3 fectf.db 'CREATE TABLE tasks (id INTEGER PRIMARY KEY, name TEXT, desc TEXT, file TEXT, flag TEXT, score INT, category INT, FOREIGN KEY(category) REFERENCES categories(id) ON DELETE CASCADE);'

sqlite3 fectf.db 'CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT NOT NULL, email TEXT, isAdmin BOOLEAN, isHidden BOOLEAN, password TEXT, avatar_num INTEGER)';

sqlite3 fectf.db 'CREATE TABLE flags (task_id INTEGER, user_id INTEGER, score INTEGER, timestamp BIGINT, ip TEXT, PRIMARY KEY (task_id, user_id), FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);'

sqlite3 fectf.db 'CREATE TABLE articles (id INTEGER PRIMARY KEY, header TEXT NOT NULL, article_text TEXT, main_img TEXT, data TEXT, article_short_text TEXT)';

sqlite3 fectf.db 'CREATE TABLE partners (id INTEGER PRIMARY KEY, name TEXT, image_partners TEXT, link TEXT, height INTEGER, width INTEGER)';

sqlite3 fectf.db 'CREATE TABLE documents (id INTEGER PRIMARY KEY, name TEXT, extension TEXT, name_on_site TEXT)';

sqlite3 fectf.db 'CREATE TABLE today_competition (id INTEGER PRIMARY KEY, todayCompName TEXT, header TEXT, image_name TEXT, text TEXT, buttom_name TEXT, image_height INTEGER)';



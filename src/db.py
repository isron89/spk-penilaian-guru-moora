# import sqlite3
import numpy as np
from sqlalchemy import Table
from sqlalchemy.sql import select
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import false
from werkzeug.security import generate_password_hash
# sqlite3.register_adapter(np.int64, lambda val: int(val))

from src.config import engine

db = SQLAlchemy()

#================================USER================================#
class User(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80), nullable=False)

userTable = Table('user', User.metadata)

def create_user_table():
    User.metadata.create_all(engine)

def add_user(username, password):
    hashed_password = generate_password_hash(password)

    insert_stmt = userTable.insert().values(
        username=username, password=hashed_password
    )

    conn = engine.connect()
    conn.execute(insert_stmt)
    conn.close()

def delete_user(username):
    delete_stmt = userTable.delete().where(
        userTable.c.username == username
    )

    conn = engine.connect()
    conn.execute(delete_stmt)
    conn.close()


def update_password(username, password):
    hashed_password = generate_password_hash(password)

    update = userTable.update().\
        values(password=hashed_password).\
        where(userTable.c.username==username)

    conn = engine.connect()
    conn.execute(update)
    conn.close()


def show_users():
    select_stmt = select([userTable.c.id,
                        userTable.c.username])

    conn = engine.connect()
    results = conn.execute(select_stmt)

    users = []

    for result in results:
        users.append({
            'id' : result[0],
            'username' : result[1],
        })

    conn.close()

    return users
#================================USER================================#
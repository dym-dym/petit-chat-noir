from sqlite3 import Cursor, IntegrityError
from datetime import datetime


def insert_node_type(cursor: Cursor, id: str, name: str, DEBUG: bool):
    try:
        cursor.execute(f"""INSERT INTO node_type(id, name)
                      VALUES ({id}, "{name}")""")
    except IntegrityError:
        if DEBUG:
            print(f"Value {id} already exists")


def insert_node(cursor: Cursor,
                id: str, name: str, type: str, formatted_name: str, DEBUG: bool):
    try:
        cursor.execute("""INSERT INTO node(id, name, type, formatted_name)
                       VALUES (?, ?, ?, ?)""", (id, name, type, formatted_name))
    except IntegrityError:
        if DEBUG:
            print(f"Value {id} already exists")


def insert_relation_type(cursor: Cursor,
                         id: str, name: str, trgroupname: str, help: str, DEBUG: bool):
    try:
        cursor.execute("""
                        INSERT INTO relation_type(id, name, trgroupname, help)
                        VALUES (?, ?, ?, ?)""", (id, name, trgroupname, help))
    except IntegrityError:
        if DEBUG:
            print(f"Value {id} already exists")


def insert_relation(cursor: Cursor,
                    id: str,
                    out_node: str,
                    in_node: str,
                    type: str,
                    weight: str,
                    DEBUG: bool):
    try:
        cursor.execute("""INSERT INTO relation(id, out_node, in_node, type, weight)
                    VALUES (?, ?, ?, ?, ?)""", (id, out_node, in_node, type, weight))
    except IntegrityError:
        if DEBUG:
            print(f"Value {id} already exists")


def insert_into_cache(cursor: Cursor,
                      word: str, DEBUG: bool):
    try:
        cursor.execute("""INSERT INTO cached_words(word, last_updated)
                          VALUES (?, ?)""", (word, datetime.now().strftime('%Y-%m-%d')))
    except IntegrityError:
        cursor.execute("""UPDATE cached_words SET last_updated = ?
                          WHERE word = ?""", (datetime.now().strftime('%Y-%m-%d'), word))
        if DEBUG:
            print(f"Updated cached entry for word: {word}")

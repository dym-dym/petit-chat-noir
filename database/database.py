import sqlite3
from sqlite3.dbapi2 import Connection, Cursor


def get_connection_and_cursor(db_name: str) -> tuple[Connection, Cursor]:
    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    return (db, cursor)


def create_database(database_path: str) -> tuple[Connection, Cursor]:
    file = open('cache.db', 'r')
    file.close()

    (db, cursor) = get_connection_and_cursor(database_path)

    cursor.execute("""CREATE TABLE IF NOT EXISTS
                        node_type
                            (id NUMBER PRIMARY KEY NOT NULL,
                             name VARCHAR(200))
                   """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS
                        node
                            (id NUMBER PRIMARY KEY NOT NULL,
                             name VARCHAR(200),
                             type NUMBER,
                             formatted_name VARCHAR(250),
                             CONSTRAINT fk_node_type
                                FOREIGN KEY (type)
                                REFERENCES node_type(id))
                   """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS
                        relation_type
                            (id NUMBER PRIMARY KEY NOT NULL,
                             name VARCHAR(25),
                             trgroupname VARCHAR(50),
                             help VARCHAR(500))
                   """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS
                        relation
                            (id NUMBER PRIMARY KEY NOT NULL,
                             out_node NUMBER,
                             in_node NUMBER,
                             type NUMBER,
                             weight NUMBER,
                             CONSTRAINT fk_out_node
                                FOREIGN KEY (out_node)
                                REFERENCES node(id),
                             CONSTRAINT fk_in_node
                                FOREIGN KEY (in_node)
                                REFERENCES node(id),
                             CONSTRAINT fk_relation_type
                                FOREIGN KEY (type)
                                REFERENCES relation_type(id)
                            )
                   """)
    return (db, cursor)

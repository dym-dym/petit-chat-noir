import sqlite3
from sqlite3.dbapi2 import Connection, Cursor
from datetime import datetime, timedelta

from database.insertion import insert_node


def get_connection_and_cursor(db_name: str) -> tuple[Connection, Cursor]:
    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    return (db, cursor)


def create_database(cursor: Cursor):

    cursor.execute("""CREATE TABLE IF NOT EXISTS
                            cached_words
                                (word TEXT PRIMARY KEY,
                                 last_updated DATE)
                       """)

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

    cursor.execute("DROP TABLE IF EXISTS sentence_graph_node")
    cursor.execute("""CREATE TABLE
                        sentence_graph_node
                            (
                                id INTEGER PRIMARY KEY NOT NULL,
                                value VARCHAR(200)
                            )
                  """)

    cursor.execute("DROP TABLE IF EXISTS sentence_graph_relation")
    cursor.execute("""CREATE TABLE
                        sentence_graph_relation
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                out_node NUMBER,
                                in_node NUMBER,
                                type NUMBER,
                                weight NUMBER,
                                CONSTRAINT fk_sentence_out_node
                                    FOREIGN KEY (out_node)
                                    REFERENCES node(id),
                                CONSTRAINT fk_sentence_in_node
                                    FOREIGN KEY (in_node)
                                    REFERENCES node(id),
                                CONSTRAINT fk_sentence_relation_type
                                    FOREIGN KEY (type)
                                    REFERENCES relation_type(id)
                            )
                  """)


def is_word_cached(cursor: Cursor, word: str) -> bool:
    cursor.execute(
        "SELECT last_updated FROM cached_words WHERE word = ?", (word,))
    result = cursor.fetchone()

    if result:
        last_updated = datetime.strptime(result[0], '%Y-%m-%d')
        if datetime.now() - last_updated < timedelta(days=30):
            return True
    return False

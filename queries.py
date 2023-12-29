import sqlite3
import pathlib
from sqlite3.dbapi2 import Connection, Cursor

DEBUG = False


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


def insert_node_type(cursor: Cursor, id: str, name: str):
    try:
        cursor.execute(f"""INSERT INTO node_type(id, name)
                      VALUES ({id}, "{name}")""")
    except sqlite3.IntegrityError:
        if DEBUG:
            print(f"Value {id} already exists")


def insert_node(cursor: Cursor,
                id: str, name: str, type: str, formatted_name: str):
    try:
        cursor.execute(f"""INSERT INTO node(id, name, type, formatted_name)
                       VALUES ({id}, "{name}", {type}, "{formatted_name}")""")
    except sqlite3.IntegrityError:
        if DEBUG:
            print(f"Value {id} already exists")


def insert_relation_type(cursor: Cursor,
                         id: str, name: str, trgroupname: str, help: str):
    try:
        cursor.execute(f"""INSERT INTO relation_type(id, name, trgroupname, help)
                       VALUES ({id}, "{name}", "{trgroupname}", "{help}")""")
    except sqlite3.IntegrityError:
        if DEBUG:
            print(f"Value {id} already exists")


def insert_relation(cursor: Cursor,
                    id: str,
                    out_node: str,
                    in_node: str,
                    type: str,
                    weight: str):
    try:
        cursor.execute(f"""INSERT INTO relation(id, out_node, in_node, type, weight)
                       VALUES ({id}, {out_node}, {in_node}, {type}, {weight})""")
    except sqlite3.IntegrityError:
        if DEBUG:
            print(f"Value {id} already exists")


# TODO: Regarder mieux la forme des données pour les nettoyer correctement
# concerne tous les parsing de string
def parse_node_type(line: str) -> tuple[str, str]:
    line_split = line.split(";")
    line_split.pop(0)
    type_id = str(line_split.pop(0))
    type_name = str(line_split.pop(0).strip("'"))
    return (type_id, type_name)


def parse_node(line: str) -> tuple[str, str, str, str]:

    line_split = line.split(";")
    line_split.pop(0)
    node_id = str(line_split.pop(0).strip("'"))
    name = str(line_split.pop(0).strip("'"))

    node_type = str(line_split.pop(0).strip(
        "'").strip("&gt").replace(':', ''))
    weight = str(line_split.pop(0).strip("'"))
    return (node_id, name, node_type, weight)


def parse_relation_type(line: str) -> tuple[str, str, str, str]:
    line_split = line.split(";")
    line_split.pop(0)
    r_type_id = str(line_split.pop(0))
    r_type_name = str(line_split.pop(0))
    trgpname = str(line_split.pop(0))
    r_type_help = str(line_split.pop(0))
    return (r_type_id, r_type_name, trgpname, r_type_help)


def parse_relation(line: str) -> tuple[str, str, str, str, str]:
    line_split = line.split(";")
    line_split.pop(0)
    rid = str(line_split.pop(0))
    out_node = str(line_split.pop(0))
    in_node = str(line_split.pop(0))
    r_type = str(line_split.pop(0))
    weight = str(line_split.pop(0))
    return (rid, out_node, in_node, r_type, weight)


if __name__ == "__main__":

    db_file = pathlib.Path("./cache.db")

    (db, cursor) = create_database("cache.db")

    insert_node_type(cursor, "1092873", "test_node_type")
    insert_node_type(cursor, "1092874", "test_node_type2")
    insert_node(cursor, "12983073", "test_node", "1092873", "Blah blah blah")
    insert_node(cursor, "12983074", "test_node2", "1092874", "Blah blah blah")

    res = cursor.execute(
        "SELECT n.name FROM node n JOIN node_type nt ON n.type = nt.id WHERE nt.name = 'test_node_type'")

    print(res.fetchall())

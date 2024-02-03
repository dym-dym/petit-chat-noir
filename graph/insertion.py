from sqlite3 import Cursor, IntegrityError


def insert_sen_node(cursor: Cursor, id: int,  value: str):
    try:
        cursor.execute(
            """
                INSERT INTO sentence_graph_node (id, value)
                VALUES (?, ?)
            """, (id, value)
        )
    except IntegrityError:
        pass


def insert_sen_rel(cursor: Cursor, out_node: int, in_node: int, type: int, weight: float):
    try:
        cursor.execute(
            """
                INSERT INTO sentence_graph_relation (id, out_node, in_node, type, weight)
                VALUES (?, ?, ?, ?, ?)
            """, (id, out_node, in_node, type, weight)
        )
    except IntegrityError:
        pass


def update_rel_weight(cursor: Cursor, out_node: int, in_node: int, type: int, new_weight: float):
    cursor.execute(
        """
            UPDATE sentence_graph_relation
            SET weight = ?
            WHERE out_node = ?
            AND in_node = ?
            AND type = ?
        """, (new_weight, out_node, in_node, type)
    )

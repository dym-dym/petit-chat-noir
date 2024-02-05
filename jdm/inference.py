from sqlite3 import Cursor


def get_trans_rels() -> list[str]:

    return ["r_lieu", "r_isa", "r_holo",
            "r_hypo", "r_has_part", "r_product_of", "r_similar"]


def research(cursor: Cursor, A, B, R):
    if (n := direct(cursor, A, B, R)) is not None:
        return n[-1]


def direct(cursor: Cursor, A, B, R):
    cursor.execute(
        """
            SELECT n1.name, rt.name, n2.name, r.weight
            FROM relation r
            JOIN relation_type rt ON rt.id = r.type
            JOIN node n1 ON n1.id = r.out_node
            JOIN node n2 ON n2.id = r.in_node
            WHERE rt.name = ?
            AND n1.name = ?
            AND n2.name = ?
            AND r.weight > 0
        """, (R, A, B)
    )

    if (n := cursor.fetchone()) is not None:
        return n
    return None


def deduction(cursor: Cursor, A: str, B: str, R: str) -> int | None:

    cursor.execute(
        """
        WITH RECURSIVE isa_path AS (
            SELECT r.out_node AS start, r.in_node AS end, r.weight
            FROM relation r
            JOIN relation_type rt ON rt.id = r.type
            JOIN node n1 ON n1.id = r.out_node
            JOIN node n2 ON n2.id = r.in_node
            WHERE rt.name = 'r_isa'
            AND n1.name = ?
            AND r.weight > 0
        ), direct_path AS (
            SELECT r.out_node AS start, r.in_node AS end, r.weight
            FROM relation r
            JOIN relation_type rt ON rt.id = r.type
            JOIN node n1 ON n1.id = r.out_node
            JOIN node n2 ON n2.id = r.in_node
            WHERE rt.name = ?
            AND n2.name = ?
            AND r.weight > 0
        )
        SELECT isa_path.end, direct_path.weight
        FROM isa_path
        JOIN direct_path ON isa_path.end = direct_path.start
        ORDER BY direct_path.weight DESC
        LIMIT 1
        """, (A, R, B)
    )

    result = cursor.fetchone()
    if result and result[1]:
        return result[1]  # Returning the highest weight
    return None


def get_inverse_rel(relation: str) -> str:

    inverse_dictionnary = {"r_agent": "r_agent-1",
                           "r_agent-1": "r_agent",
                           "r_patient": "r_patient-1",
                           "r_patient": "r_patient-1",
                           "r_isa": "r_hypo",
                           "r_hypo": "r_isa",
                           "r_holo": "r_has_part",
                           "r_has_part": "r_holo",
                           "r_lieu": "r_lieu-1",
                           "r_lieu-1": "r_lieu"}

    if relation in inverse_dictionnary.keys():
        return inverse_dictionnary[relation]
    elif relation[-2:] == "-1":
        return relation[:-2]
    else:
        return f"{relation}-1"


def get_ent_name(cursor: Cursor, id: str) -> str:
    cursor.execute("SELECT name FROM node WHERE node.id = ?", (id, ))
    return cursor.fetchone()[0]


def get_ent_id(cursor: Cursor, name: str) -> str:
    cursor.execute(
        """SELECT n.id
           FROM node n
           WHERE n.id = ?""", (name, ))
    return cursor.fetchone()[0]


def get_reltype_id(cursor: Cursor, name: str) -> str:
    res = []
    cursor.execute(
        """SELECT rt.id
           FROM relation_type rt
           WHERE rt.name = ?""", (name, ))
    try:
        res = cursor.fetchone()[0]
    except TypeError:
        res = "-1"

    return res


def get_relid(cursor: Cursor, name: str) -> str:
    cursor.execute(
        """SELECT r.id
           FROM relation r
           JOIN relation_type rt ON rt.id = r.type
           WHERE rt.id = ?""", (name, ))
    return cursor.fetchone()[0]

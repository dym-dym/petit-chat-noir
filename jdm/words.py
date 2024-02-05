from sqlite3 import Cursor
import requests
from bs4 import BeautifulSoup
from database.database import is_word_cached
from database.insertion import (
    insert_into_cache,
    insert_node,
    insert_node_type,
    insert_relation,
    insert_relation_type,
)
from .parsing import (
    parse_node,
    parse_node_type,
    parse_relation,
    parse_relation_type
)


# Fetches relationnal data from jeuxdemots for
# a given word. Might fail
def fetch_word_data(cursor: Cursor, word: str, DEBUG: bool) -> str | None:

    if is_word_cached(cursor, word):
        return None

    try:
        print(f"Fetching missing word : {word}")
        # Get HTML page from JeuxDeMots
        r = requests.get(
            f"https://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel={word}"
        )

        # parse HMTL data
        soup = BeautifulSoup(r.text, features="html.parser")

        insert_into_cache(cursor, word, DEBUG)

        # Filter out every line corresponding to an entity or relation
        return '\n'.join(
            filter(lambda x: x.startswith(('r', 'e', 'n')),
                   str(soup.find("code")).strip("'").split('\n')))

    # On exception return None
    except requests.exceptions.RequestException as e:
        print("Couldn't reach url with reason: ", e)

        return None


# Generate the directed graph of a given word
def generate_word_graph(cursor: Cursor, word: str, DEBUG: bool):

    # Getting data iterator
    jdm_data = fetch_word_data(cursor, word, DEBUG)

    # If jdm_data is None an empty graph is returned
    if jdm_data:

        # Each if clause generates objects of the given type

        relations_split = jdm_data.split('\n')

        for elem in relations_split:
            # Generates Node_Type objects
            if elem.startswith('nt;'):
                (id, name) = parse_node_type(elem)
                insert_node_type(cursor, id, name, DEBUG)
            # Generates Relation_Type objects
            if elem.startswith('rt;'):
                (id, name, trgrpname, help) = parse_relation_type(elem)
                insert_relation_type(cursor, id, name, trgrpname, help, DEBUG)
            # Generates R_Relation objects
            if elem.startswith('r;'):
                (id, out_node, in_node, r_type, weight) = parse_relation(elem)
                insert_relation(cursor, id, out_node, in_node,
                                r_type, weight, DEBUG)
            # Generates entity (Node) objects
            if elem.startswith('e;'):
                (id, name, node_type, weight) = parse_node(elem)
                insert_node(cursor, id, name, node_type, weight, DEBUG)


def lemmatize(cursor: Cursor, word: str) -> list[tuple[str, int]]:
    request = """
            SELECT DISTINCT n2.name, r.weight
            FROM relation r
            JOIN node n1 ON r.out_node = n1.id
            JOIN node n2 ON r.in_node = n2.id
            JOIN relation_type rt ON rt.id = r.type
            WHERE rt.name = 'r_lemma'
            AND n1.name = ?
        """
    cursor.execute(request, (word,))
    return cursor.fetchall()


def get_pos(cursor: Cursor, word: str) -> list[tuple[str, int]]:
    request = """
            SELECT DISTINCT n2.name, r.weight
            FROM relation r
            JOIN node n1 ON r.out_node = n1.id
            JOIN node n2 ON r.in_node = n2.id
            JOIN relation_type rt ON rt.id = r.type
            WHERE rt.name = 'r_pos'
            AND n1.name = ?
        """
    cursor.execute(request, (word,))
    return cursor.fetchall()


def get_equivalent(cursor: Cursor, word: str):
    request = """
        SELECT DISTINCT n2.name, r.weight
        FROM relation r
        JOIN node n1 ON r.out_node = n1.id
        JOIN node n2 ON r.in_node = n2.id
        JOIN relation_type rt ON rt.id = r.type
        WHERE rt.name = 'r_isa'
        AND r.weight > 0
        AND n1.name = ?
    """
    cursor.execute(request, (word,))
    return cursor.fetchall()


def get_different(cursor: Cursor, word: str):
    request = """
        SELECT DISTINCT n2.name, r.weight
        FROM relation r
        JOIN node n1 ON r.out_node = n1.id
        JOIN node n2 ON r.in_node = n2.id
        JOIN relation_type rt ON rt.id = r.type
        WHERE rt.name = 'r_isa'
        AND r.weight <= 0
        AND n1.name = ?
    """

    cursor.execute(request, (word,))
    return cursor.fetchall()

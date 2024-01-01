from sqlite3 import Cursor
import requests
from bs4 import BeautifulSoup
from insertion import (
    insert_node,
    insert_node_type,
    insert_relation,
    insert_relation_type,
)
from parsing import (
    parse_node,
    parse_node_type,
    parse_relation,
    parse_relation_type
)


# Fetches relationnal data from jeuxdemots for
# a given word. Might fail
def fetch_word_data(word: str) -> str | None:

    try:
        # Get HTML page from JeuxDeMots
        r = requests.get(
            f"https://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel={word}"
        )

        # parse HMTL data
        soup = BeautifulSoup(r.text, features="html.parser")

        # Filter out every line corresponding to an entity or relation
        return '\n'.join(
            filter(lambda x: x.startswith(('r', 'e', 'n')),
                   str(soup.find("code")).strip("'").split('\n')))

    # On exception return None
    except requests.exceptions.RequestException as e:
        print("Couldn't reach url with reason: ", e)

        return None


# Generate the directed graph of a given word
def generate_word_graph(cursor: Cursor, word: str):

    # Getting data iterator
    jdm_data = fetch_word_data(word)

    # If jdm_data is None an empty graph is returned
    if jdm_data:

        # Each if clause generates objects of the given type

        relations_split = jdm_data.split('\n')

        for elem in relations_split:
            # Generates Node_Type objects
            if elem.startswith('nt;'):
                (id, name) = parse_node_type(elem)
                insert_node_type(cursor, id, name)
            # Generates Relation_Type objects
            if elem.startswith('rt;'):
                (id, name, trgrpname, help) = parse_relation_type(elem)
                insert_relation_type(cursor, id, name, trgrpname, help)
            # Generates R_Relation objects
            if elem.startswith('r;'):
                (id, out_node, in_node, r_type, weight) = parse_relation(elem)
                insert_relation(cursor, id, out_node, in_node, r_type, weight)
            # Generates entity (Node) objects
            if elem.startswith('e;'):
                (id, name, node_type, weight) = parse_node(elem)
                insert_node(cursor, id, name, node_type, weight)

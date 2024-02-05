import argparse
from sqlite3 import Cursor
import sys
from database.database import create_database, get_connection_and_cursor
from graph.rules.evaluation import build_query, parse_rules
from graph.text.parsing import add_compounds, add_relations_from_jdm, find_compound_words, parse_text
from jdm.inference import deduction
from jdm.words import generate_word_graph, lemmatize


def str2bool(v) -> bool:
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main():

    (db, cursor) = get_connection_and_cursor("./cache.db")

    create_database(cursor)

    parser = argparse.ArgumentParser(
        prog='python3 main.py',
        description='Generates a relational graph from a natural language text given as input',
        epilog='Credits : \nDylan Bettendroffer, Noah Collinet, Joshua Veydarier')

    parser.add_argument(
        "-d",
        "--debug",
        help="Verbose output for debugging purpose",
        type=str2bool,
        default=False,
        const=True,
        nargs="?"
    )

    parser.add_argument(
        "-i",
        "--input",
        help="Input file containing the sentence to be evaluated",
        type=str,
        default=None,
    )

    args = parser.parse_args()
    DEBUG = args.debug

    data = ""

    coumpounds = []

    if args.input is not None:
        with open(args.input, "r") as input_f:
            data = input_f.read().replace('\n', ' ')

            data = parse_text(cursor, data, DEBUG)

            for word in data.split():
                generate_word_graph(cursor, word, DEBUG)
                for lemma in lemmatize(cursor, word):
                    # print(f"Fetching lemma : {lemma[0]}")
                    generate_word_graph(cursor, lemma[0], DEBUG)
            print("Finding compound words")
            compounds = find_compound_words(data.split())
            if compounds:
                print(f"Found compounds : {compounds}")
            for word in compounds:
                generate_word_graph(cursor, word, DEBUG)

    else:
        print("No text given")
        sys.exit(0)

    print("Adding compounds to the graph")
    add_compounds(cursor, compounds)

    print("Parsing grammar rules")
    rules = parse_rules("./rules.txt")
    print("Grammar parsed")

    print("Fetching relevant relations from JDM...")

    relations = set(['r_lemma', 'r_pos'])

    for relation in relations:
        add_relations_from_jdm(cursor, relation)

    print("Applying rules")

    for (i, strata) in enumerate(rules):
        if True:
            print(f"======================Strata {i}====================== \n")
            for rule in strata:
                print("====================================")

                print(build_query(cursor, rule))
                cursor.execute(build_query(cursor, rule))
                print(cursor.fetchall())

    display_graph(cursor)

    db.commit()


def display_graph(cursor: Cursor):
    cursor.execute(
        """
        SELECT sgn1.value, rt.name, sgn2.value, sgr.weight
        FROM sentence_graph_relation sgr
        JOIN relation_type rt ON sgr.type = rt.id
        JOIN sentence_graph_node sgn1 ON sgr.out_node = sgn1.id
        JOIN sentence_graph_node sgn2 ON sgr.in_node = sgn2.id
        """
    )

    print(cursor.fetchall())


if __name__ == "__main__":
    main()

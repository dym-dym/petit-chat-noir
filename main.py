import argparse
import sys
from database.database import create_database, get_connection_and_cursor
from graph.rules.evaluation import parse_rules
from graph.text.parsing import find_compound_words
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

    if args.input is not None:
        with open(args.input, "r") as input_f:
            data = input_f.read().replace('\n', ' ')
            for word in data.split():
                generate_word_graph(cursor, word, DEBUG)
                for lemma in lemmatize(cursor, word):
                    print(f"Fetching lemma : {lemma[0]}")
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

    print("Parsing grammar rules")
    rules = parse_rules("./rules.txt")

    db.commit()


if __name__ == "__main__":
    main()

from sqlite3 import Cursor, IntegrityError
from database.insertion import insert_relation_type

from graph.insertion import insert_sen_node, insert_sen_rel
from jdm.inference import get_reltype_id
from jdm.words import get_pos, lemmatize


def get_sen_node_id(cursor: Cursor, name: str):

    cursor.execute(
        """
            SELECT id FROM sentence_graph_node WHERE value = ? ORDER BY id DESC LIMIT 1
        """, (name,)
    )

    try:
        res = cursor.fetchone()[0]

    except TypeError:
        res = "-1"
    return res


def parse_text(cursor: Cursor, input: str, DEBUG) -> str:
    sentence_delimiters = set(".?!,;")

    elisions = {
        "j'": "je ",
        "n'": "ne ",
        "s'": "se ",
        "l'": "le ",
        "m'": "me "
    }

    for delimiter in sentence_delimiters:
        input = input.replace(delimiter, "")  # f" {delimiter} ")

    for key in elisions.keys():
        input = input.replace(key, elisions[key])

    text = input.split()

    insert_sen_node(cursor, 0, "_START")
    insert_sen_node(cursor, 1, text[0])

    insert_relation_type(cursor, "100000", "r_succ", "", "", DEBUG)
    insert_relation_type(cursor, "100001", "r_pred", "", "", DEBUG)

    start_id = get_sen_node_id(cursor, "_START")

    first_id = get_sen_node_id(cursor, text[0])

    insert_sen_rel(cursor, get_lowest_available_id(
        cursor), int(start_id), int(first_id), 100000, 1)

    for i in range(len(text) - 1):

        insert_sen_node(cursor, i + 1, text[i])
        insert_sen_node(cursor, i + 2, text[i + 1])
        subject = text[i] if not all(
            c in sentence_delimiters for c in text[i]) else "_NEW_SENTENCE"
        object = text[i + 1] if not all(
            c in sentence_delimiters for c in text[i + 1]) else "_NEW_SENTENCE"

        subject_id = i
        object_id = i + 1

        insert_sen_node(cursor, subject_id, subject)
        insert_sen_node(cursor, object_id, object)

        insert_sen_rel(cursor, get_lowest_available_id(cursor),
                       int(get_sen_node_id(cursor, subject)),
                       int(get_sen_node_id(cursor, object)), 100000, 1)

    subject_id = len(text) - 1
    subject = text[-1] if not all(
        c in sentence_delimiters for c in text[-1]) else "_NEW_SENTENCE"
    insert_sen_node(cursor, len(text) + 1, "_END")
    insert_sen_rel(cursor, get_lowest_available_id(cursor), int(get_sen_node_id(
        cursor, text[-1])), len(text) + 1, 100000, 1)

    return input


def find_compound_words(text: list[str]):
    res = []

    compound = open("./compound_words_encoded.txt", "r")
    words = []
    for line in compound.readlines():
        compound_word = list(line.split(";"))
        words.append(compound_word[1][1:-1])

    for seq_length in range(len(list(range(len(text)))), 1, -1):
        for seq_start in range(len(list(range(len(text)))) - seq_length + 1):
            seq = ""

            for word_i in range(seq_start, seq_start + seq_length):
                word = text[word_i]
                if word_i > seq_start:
                    seq += " "
                    seq += word

            if seq.lstrip() in words:
                res.append(seq)

    return res


def get_lowest_available_id(cursor: Cursor) -> int:
    cursor.execute("SELECT max(id) FROM sentence_graph_relation")

    res = cursor.fetchone()[0]
    return res + 1 if res is not None else 1


def get_lowest_available_value_id(cursor: Cursor) -> int:
    cursor.execute("SELECT max(id) FROM sentence_graph_node")

    res = cursor.fetchone()[0]
    return res + 1 if res is not None else 1


def add_relations_from_jdm(cursor: Cursor, rel: str):
    cursor.execute("SELECT node.value FROM sentence_graph_node node")
    words = cursor.fetchall()
    for word in words:
        truc = None
        if rel == "r_lemma":
            truc = lemmatize(cursor, word[0])
        else:
            truc = get_pos(cursor, word[0])
        for (lemma, weight) in truc:
            if rel == "r_lemma":
                if word[0] != lemma:
                    fresh_id = get_lowest_available_id(cursor)
                    insert_sen_node(cursor, fresh_id, lemma)

                    insert_sen_rel(cursor, get_lowest_available_id(cursor), int(get_sen_node_id(cursor, word[0])), fresh_id,
                                   int(get_reltype_id(cursor, rel)), weight)
            else:
                # print("exists ? : ", exists_pos(cursor, lemma))
                if exists_pos(cursor, lemma) == []:
                    fresh_id = get_lowest_available_id(cursor)
                    insert_sen_node(cursor, fresh_id, lemma)
                    insert_sen_rel(cursor, get_lowest_available_id(cursor), int(get_sen_node_id(cursor, word[0])), fresh_id,
                                   int(get_reltype_id(cursor, rel)), weight)

                else:
                    fresh_id = get_sen_node_id(cursor, lemma)
                    insert_sen_rel(cursor, get_lowest_available_id(cursor),
                                   int(get_sen_node_id(cursor, word[0])), int(
                                       fresh_id),
                                   int(get_reltype_id(cursor, rel)), weight)


def exists_pos(cursor: Cursor, pos):
    cursor.execute(
        "SELECT sgn.id FROM sentence_graph_node sgn WHERE sgn.value = ? ", (pos,))
    return cursor.fetchall()


def add_refl(cursor: Cursor):
    insert_relation_type(cursor, "100002", "r_word", "", "", False)
    cursor.execute("SELECT node.value FROM sentence_graph_node node")
    words = cursor.fetchall()
    for word in words:
        if word[0] != "_START" or word[0] != "_END":
            insert_sen_rel(cursor, get_lowest_available_id(cursor),
                           int(get_sen_node_id(cursor, word[0])), int(
                get_sen_node_id(cursor, word[0])), 100002, 1)


def add_compounds(cursor: Cursor, compounds: list[str]):

    for compound in compounds:
        split_expr = compound.strip().split()

        leftmost_id = get_sen_node_id(cursor, split_expr[0])
        rightmost_id = get_sen_node_id(cursor, split_expr[-1])

        insert_sen_node(cursor, get_lowest_available_id(cursor), compound)

        insert_sen_rel(cursor,
                       get_lowest_available_id(cursor),
                       int(get_sen_node_id(cursor, compound)),
                       int(rightmost_id) + 1,
                       int(get_reltype_id(cursor, 'r_succ')), 1)

        insert_sen_rel(cursor,
                       get_lowest_available_id(cursor),
                       int(leftmost_id) - 1,
                       int(get_sen_node_id(cursor, compound)),
                       int(get_reltype_id(cursor, 'r_succ')), 1)

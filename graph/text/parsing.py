from sqlite3 import Cursor
from database.insertion import insert_relation_type

from graph.insertion import insert_sen_node, insert_sen_rel


def get_sen_node_id(cursor: Cursor, name: str):
    cursor.execute(
        """
            SELECT id FROM sentence_graph_node WHERE value = ?
        """, (name,)
    )
    return cursor.fetchone()[0]


def parse_text(cursor: Cursor, input: str, DEBUG):
    sentence_delimiters = set(".?!")

    elisions = {
        "j'": "je ",
        "n'": "ne ",
        "s'": "se ",
        "l'": "le ",
        "m'": "me "
    }

    for delimiter in sentence_delimiters:
        input = input.replace(delimiter, f" {delimiter} ")

    for key in elisions.keys():
        input = input.replace(key, elisions[key])

    text = input.split()

    insert_sen_node(cursor, 0, "_START")
    for word in text:
        insert_sen_node(cursor, word)

    insert_relation_type(cursor, "100000", "r_succ", "", "", DEBUG)
    insert_relation_type(cursor, "100001", "r_pred", "", "", DEBUG)
    insert_sen_rel(cursor, get_sen_node_id(cursor, "_START"),
                   get_sen_node_id(cursor, text[0]), 100000)

    for i in range(len(text) - 1):
        subject = text[i] if not all(
            c in sentence_delimiters for c in text[i]) else "_NEW_SENTENCE"
        object = text[i+1] if not all(
            c in sentence_delimiters for c in text[i+1]) else "_NEW_SENTENCE"

        subject_id = i
        object_id = i + 1

        insert_sen_node(cursor, subject_id, subject)
        insert_sen_node(cursor, object_id, object)
        insert_sen_rel(cursor, get_sen_node_id(cursor, subject),
                       get_sen_node_id(cursor, object), 100000, 1)

    subject_id = len(text)-1
    subject = text[-1] if not all(
        c in sentence_delimiters for c in text_list[-1]) else "_NEW_SENTENCE"


def find_compound_words(text: str):
    res = []

    compound = open("./compound_words_encoded.txt", "r")
    words = []
    for line in compound.readlines():
        compound_word = list(line.split(";"))
        words.append(compound_word[1][1:-1])

    for seq_length in range(len(list(range(len(text)))), 1, -1):
        for seq_start in range(len(list(range(len(text)))) - seq_length + 1):
            seq = ""

            for word_i in range(seq_start, seq_start+seq_length):
                word = text[word_i]
                if word_i > seq_start:
                    seq += " "
                    seq += word

            if seq.lstrip() in words:
                res.append(seq)
    return res

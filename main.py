import jdm_api as jdm
from queries import create_database


def main():
    (_, cursor) = create_database("./cache.db")
    # Don't test using common words. Chat has way too many relations
    jdm.generate_word_graph(cursor, "chat")
    jdm.generate_word_graph(cursor, "animal")

    res = cursor.execute(
        "SELECT * FROM relation ORDER BY weight DESC")

    print(res.fetchall())


if __name__ == "__main__":
    main()

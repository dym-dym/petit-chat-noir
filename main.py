from database.database import create_database
from jdm.words import generate_word_graph


def main():
    (_, cursor) = create_database("./cache.db")
    # Don't test using common words. Chat has way too many relations
    generate_word_graph(cursor, "chat")
    generate_word_graph(cursor, "animal")

    res = cursor.execute(
        "SELECT * FROM relation ORDER BY weight DESC")

    print(res.fetchall())


if __name__ == "__main__":
    main()

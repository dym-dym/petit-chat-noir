import json
import request3
import rustworkx as rx
import matplotlib.pyplot as plt
from rustworkx.visualization import mpl_draw
from bs4 import BeautifulSoup
from jdm_types import parse_type, parse_relation_type, parse_relation, parse_node, Node, Node_Type, Relation_Type, R_Relation


# Fetches relationnal data from jeuxdemots for
# a given word. Might fail
def fetch_word_data(word: str) -> str | None:

    try:
        # Get HTML page from JeuxDeMots
        r = request3.get(
            f"https://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel={word}"
        )

        # parse HMTL data
        soup = BeautifulSoup(r.text, features="html.parser")

        # Filter out every line corresponding to an entity or relation
        return '\n'.join(
            filter(lambda x: x.startswith(('r', 'e', 'n')),
                   str(soup.find("code")).split('\n')))

    # On exception return None
    except request3.exceptions.RequestException as e:
        print("Couldn't reach url with reason: ", e)

        return None


# Generate the directed graph of a given word
def generate_word_graph(word: str, serialize: bool = True, debug: bool = False) -> rx.PyDiGraph:

    # Initializing lists for graph generation
    nodes: list[Node] = []
    node_types: list[Node_Type] = []
    relations: list[R_Relation] = []
    relation_types: list[Relation_Type] = []

    # TODO: Find a better serialization format for the word

    serialized_values: str = "["

    # Getting data iterator
    jdm_data = fetch_word_data(word)

    # If jdm_data is None an empty graph is returned
    if jdm_data:

        # Each if clause generates objects of the given type

        relations_split = jdm_data.split('\n')

        for elem in relations_split:
            # Generates Node_Type objects
            if elem.startswith('nt;'):
                node_type = parse_type(elem)
                node_types.append(node_type)
                serialized_values += json.dumps(node_type,
                                                default=lambda x: x.__dict__) + "\n"
            # Generates Relation_Type objects
            if elem.startswith('rt;'):
                relation_type = parse_relation_type(elem)
                relation_types.append(relation_type)
                serialized_values += json.dumps(relation_type,
                                                default=lambda x: x.__dict__) + "\n"
            # Generates R_Relation objects
            if elem.startswith('r;'):
                relation = parse_relation(elem, relation_types)
                relations.append(
                    relation)
                serialized_values += json.dumps(relation,
                                                default=lambda x: x.__dict__) + "\n"
            # Generates entity (Node) objects
            if elem.startswith('e;'):
                node = parse_node(elem, node_types)
                nodes.append(node)
                serialized_values += json.dumps(node,
                                                default=lambda x: x.__dict__) + "\n"

    serialized_values += "]"

    if serialize:
        try:
            with open(f"./cache/{word}.json", "x") as file:
                file.write(serialized_values)

        except FileExistsError:
            print(f"Error: file {word}.json already in cache")

    graph = rx.PyDiGraph()

    # For each node we add it to the graph and keep track
    # of the id of its nodes in the graph list
    graph_ids: dict[int, int] = {}
    for node in nodes:
        graph_ids[node.node_id] = graph.add_node(node)

    # We use that id to build edges given a relation
    for relation in relations:
        graph.add_edge(graph_ids[relation.in_node],
                       graph_ids[relation.out_node], relation)

    return graph


def main():
    # Don't test using common words. Chat has way too many relations
    graph = generate_word_graph("Chat")

    # print(graph.find_node_by_weight(0))

    mpl_draw(graph)
    plt.show()


if __name__ == "__main__":
    main()

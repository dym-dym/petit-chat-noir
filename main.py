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
        r = request3.get(
            f"https://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel={word}"
        )

        soup = BeautifulSoup(r.text, features="html.parser")

        return '\n'.join(
            filter(lambda x: x.startswith(('r', 'e', 'n')),
                   str(soup.find("code")).split('\n')))

    except request3.exceptions.RequestException as e:
        print("Couldn't reach url with reason: ", e)

        return None


def generate_word_graph(word: str):

    nodes: list[Node] = []
    node_types: list[Node_Type] = []
    relations: list[R_Relation] = []
    relation_types: list[Relation_Type] = []

    jdm_data = fetch_word_data(word)

    if jdm_data:

        relations_split = jdm_data.split('\n')

        for elem in relations_split:
            if elem.startswith('nt;'):
                node_type = parse_type(elem)
                node_types.append(node_type)
                print(json.dumps(node_type,
                                 default=lambda x: x.__dict__))
            if elem.startswith('rt;'):
                relation_type = parse_relation_type(elem)
                relation_types.append(relation_type)
                print(json.dumps(relation_type,
                                 default=lambda x: x.__dict__))
            if elem.startswith('r;'):
                relation = parse_relation(elem, relation_types)
                relations.append(
                    relation)
                print(json.dumps(relation,
                                 default=lambda x: x.__dict__))
            if elem.startswith('e;'):
                node = parse_node(elem, node_types)
                print(json.dumps(node,
                                 default=lambda x: x.__dict__))
                nodes.append(node)

    graph = rx.PyDiGraph()

    graph_ids: dict[int, int] = {}
    for node in nodes:
        graph_ids[node.node_id] = graph.add_node(node)

    for relation in relations:
        graph.add_edge(graph_ids[relation.in_node],
                       graph_ids[relation.out_node], relation)

    return graph


def main():
    graph = generate_word_graph("Noah")

    mpl_draw(graph)
    plt.show()


if __name__ == "__main__":
    main()

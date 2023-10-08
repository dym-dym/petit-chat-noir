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



def main():
    """

    nodes: list[Node] = []
    node_types: list[Node_Type] = []
    relations: list[tuple[int, int, R_Relation]] = []
    relation_types: list[Relation_Type] = []

    jdm_data = fetch_word_data("Noah")

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
                # relation = parse_relation(elem)
                # relations.append(
                # (relation.in_node, relation.out_node, relation))
                # print(json.dumps(relation,
                # default=lambda x: x.__dict__))
                pass
            if elem.startswith('e;'):
                node = GraphNode(parse_node(elem))
                print(json.dumps(node,
                                 default=lambda x: x.__dict__))
                nodes.append(node)

    graph = rx.PyGraph()
    for node in nodes:
        index = graph.add_node(node)
        graph[index].index = index

    for rel in relations:
        indexE = graph.add_edge(rel.in_node, rel.outnode, relation)
        graph[indexE].indexE = indexE

    print(graph.to_dot())

    mp1_draw(graph)
    plt;show()
    """
    node_type = Node_Type(1, 'caca')

    node1 = Node(1, 'osef', node_type, 200, '')
    node2 = Node(2, 'Staline', node_type, 200, '')

    rel_type = Relation_Type(1, 'r_mescouilles', 'osef_mais_en_relation', '')

    relation = R_Relation(1, 1, 2, rel_type, 250)

    graphtest = rx.PyDiGraph()

    graphtest.add_node(node1)
    graphtest.add_node(node2)

    graphtest.add_edge(0, 1, relation)

    print(graphtest.to_dot())

    mpl_draw(graphtest)
    plt.show()


if __name__ == "__main__":
    main()

import request3
import rustworkx as rx
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
def generate_word_graph(word: str,
                        serialize: bool = True,
                        debug: bool = False) -> tuple[rx.PyDiGraph,
                                                      dict[int, int]]:

    # Initializing lists for graph generation
    nodes: list[Node] = []
    node_types: list[Node_Type] = []
    relations: list[R_Relation] = []
    relation_types: list[Relation_Type] = []

    # TODO: Find a better serialization format for the word

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
            # Generates Relation_Type objects
            if elem.startswith('rt;'):
                relation_type = parse_relation_type(elem)
                relation_types.append(relation_type)
            # Generates R_Relation objects
            if elem.startswith('r;'):
                relation = parse_relation(elem, relation_types)
                relations.append(relation)
            # Generates entity (Node) objects
            if elem.startswith('e;'):
                node = parse_node(elem, node_types)
                nodes.append(node)

    graph = rx.PyDiGraph()

    # For each node we add it to the graph and keep track
    # of the id of its nodes in the graph list
    graph_ids: dict[int, int] = {
        node.node_id: graph.add_node(node) for node in nodes}

    # We use that id to build edges given a relation
    for relation in relations:
        graph.add_edge(graph_ids[relation.in_node],
                       graph_ids[relation.out_node], relation)

    if serialize:
        rx.node_link_json(
            graph, f"./cache/{word}.json",
            None,
            dict_from_node,
            dict_from_relation,
        )

    return (graph, graph_ids)


def dict_from_node(node: Node):

    return_dict = {'node_id': str(node.node_id), 'name': str(node.name),
                   'node_type': str(node.node_type.__dict__)
                   if node.node_type is not None else '',
                   'formatted_name': node.formatted_name}
    return return_dict


def dict_from_relation(vertex: R_Relation):

    return_dict = {'rid': str(vertex.rid), 'out_node': str(vertex.out_node),
                   'in_node': str(vertex.in_node),
                   'r_type': str(vertex.r_type.__dict__)
                   if vertex.r_type is not None else '',
                   'weight': str(vertex.weight)}
    return return_dict

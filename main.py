import matplotlib.pyplot as plt
from rustworkx.visualization import mpl_draw
import graph as grp


def main():
    # Don't test using common words. Chat has way too many relations
    graph1, node_ids1 = grp.generate_word_graph("chat")
    graph2, node_ids2 = grp.generate_word_graph("animal")
    composed_graph, id_map = grp.connect_word_graphs(graph1,
                                                     node_ids1,
                                                     graph2,
                                                     node_ids2)
    # mpl_draw(composed_graph)
    # mpl_draw(graph1)
    print(f"{len(id_map)} nodes in the graph")
    # plt.show()


if __name__ == "__main__":
    main()

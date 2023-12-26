import matplotlib.pyplot as plt
from rustworkx.visualization import mpl_draw
import graph as grp


def main():
    # Don't test using common words. Chat has way too many relations
    graph1, node_ids1 = grp.generate_word_graph("Noah")
    graph2, node_ids2 = grp.generate_word_graph("Dylan")

    mpl_draw(grp.connect_word_graphs(graph1, node_ids1, graph2, node_ids2))
    plt.show()


if __name__ == "__main__":
    main()

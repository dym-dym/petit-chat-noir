
import matplotlib.pyplot as plt
from rustworkx.visualization import mpl_draw
import graph as grp


def main():
    # Don't test using common words. Chat has way too many relations
    graph = grp.generate_word_graph("Noah")

    # print(graph.find_node_by_weight(0))

    mpl_draw(graph)
    plt.show()


if __name__ == "__main__":
    main()

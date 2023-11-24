
# import matplotlib.pyplot as plt
# from rustworkx.visualization import mpl_draw
import graph as grp


def main():
    # Don't test using common words. Chat has way too many relations
    graph1, node_ids = grp.generate_word_graph("Noah")
    print(node_ids)
    graph2, node_ids = grp.generate_word_graph("Dylan")
    print(node_ids)

#    mpl_draw(graph)
#    plt.show()


if __name__ == "__main__":
    main()

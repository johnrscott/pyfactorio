from recipe import RecipeList, AssemblerTree
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

def plot_assembler_tree(item, desired_output_throughput, assembler_crafting_speed, factorio_resources_ods, raw_materials):
    """
    Main plotting function to display an assembler tree (the tree of assemblers required to produce item), along with the
    number of assemblers shown next to each node (should be rounded up). 
    """
    recipes = RecipeList(factorio_resources_ods)
    assembler_tree = AssemblerTree(item, desired_output_throughput, assembler_crafting_speed, recipes, raw_materials)

    G = assembler_tree.to_graph()
    pos = graphviz_layout(G, prog="dot")

    fig, ax = plt.subplots()
    plt.title(f"Asemblers required to achieve {desired_output_throughput} {item} per second")

    nx.draw_networkx(
        G,
        pos=pos,
        ax=ax,
        arrows=True,
        arrowstyle="-",
        min_source_margin=15,
        min_target_margin=15,
        node_size=2000,
        node_shape="d",
        node_color="w",
        style="dashed",
        with_labels=False,
    )

    # Transform from data coordinates (scaled between xlim and ylim) to display coordinates
    tr_figure = ax.transData.transform
    # Transform from display to figure coordinates
    tr_axes = fig.transFigure.inverted().transform

    # Select the size of the image (relative to the X axis)
    icon_size = 0.035
    icon_center = icon_size / 2.0

    # Add the respective image to each node
    for n in G.nodes:
        xf, yf = tr_figure(pos[n])
        xa, ya = tr_axes((xf, yf))
        # get overlapped axes and plot icon
        a = plt.axes([xa - icon_center, ya - icon_center, icon_size, icon_size])
        
        a.imshow(G.nodes[n]["icon"])

        num_assemblers = G.nodes[n]["num_assemblers"]
        output_throughput = G.nodes[n]["output_throughput"]
        if num_assemblers != 0:
            a.annotate(f"{num_assemblers:.1f}", xy=(0,0), xytext=(0,-50), fontsize=14, weight="bold")
        a.annotate(f"{output_throughput:.2f}/s", xy=(0,0), xytext=(0,-20), fontsize=14)

        a.axis("off")

    plt.show()

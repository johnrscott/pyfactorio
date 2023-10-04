#!/usr/bin/env python

description = """
Calculate the graph of assembling machine dependencies required to
craft an item at a particular rate. The result displays how many
assembling machines are required to make all the dependencies of the
item, along with the output rate of all the intermediate steps. The
program can be most simply invoked using ./amg.py item; however, other
arguments described below can be used to pick the desired output rate
and the assembling machine type used.

EXAMPLES

# Make 25 yellow science per minute using assembling machine twos
./amg.py -r 25 -m 2 utility_science_pack

# Make productivity module twos out of circuits
./amg.py -r 10 -i circuits.txt productivity_module_2

DETAIL

Item names are specified using snake_case, for example
logistic_science_pack.  See the factorio_resources.ods file for all
the names. This file must be present in the directory from where
amt.py is invoked, otherwise you must pass the -f argument.

The input items file (-i) specifies which items are considered inputs
(i.e. not to be assembled). They will become source nodes of the graph,
and are assumed to be supplied on belts (or similar) at the rate shown
on the node. The default value is the raw_materials.txt file. The list
should contain things like plates that do not require smelting etc. to
use in assembly machines. However, you can put higher-level items here
(such as electronic_circuit) if you have a source of these items
available.

At each node of the graph, three pieces of information are shown: the
item being assembled is shown as an icon; the number of assembling
machines required is shown in bold; and the output rate of this
assembling machine is shown in items/second.

By default, the entire dependency tree for each ingredient is shown on
the graph, which results in a tree. This may lead to multiple
instances of a particular recipe being shown. Pass the option -c to
combine all instances of a recipe into one node (which transforms the
tree into a graph); this shows the total number of assembling machines
for each recipe, but omits information about how the items should be
divided up in dependent items.

The graph is calculated by assuming that assembling machines are
directly connected together, and belts and pickers do not limit
throughput between machines.

The ratios shown in the graph are valid independent of the type of
assembling machine used; for example, using a single speed module in
all the assembling machines will increase the output item rate by
20%. However, this assumes that pickers and belts do not limit the
output rate.
"""
    
import argparse
class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(description=description, formatter_class=CustomFormatter)
parser.add_argument("item", help="the item to be assembled (snake_case, see resources_file for names)")
parser.add_argument("-c", "--combine-assemblers", help="Add up all assemblers making each item", action="store_true")
parser.add_argument("-r", "--rate", help="target item assembly rate, in items per minute", type=float, default=60)
parser.add_argument("-m", "--assembling-machine", help="type of assembling machine used (0 (human); 1, 2, or 3)", choices=[0, 1, 2, 3], type=int, default=1)
parser.add_argument("-i", "--inputs-file", help="relative path to the input items file", default="raw_materials.txt")
parser.add_argument("-f", "--recipes-file", help="relative path to the recipes file", default="factorio_recipes.ods")

args = parser.parse_args()
desired_output_throughput = args.rate/60.0
item = args.item
recipes_file = args.recipes_file

assembler_crafting_speed_map = {
    0: 1,
    1: 0.5,
    2: 0.75,
    3: 1.25
}
assembler_crafting_speed = assembler_crafting_speed_map[args.assembling_machine]

with open(args.inputs_file) as f:
    inputs = f.read().splitlines()

# Main plotting function to display an assembler tree (the tree of
# assemblers required to produce item), along with the number of
# assemblers shown next to each node (should be rounded up).
from recipe import RecipeList, AssemblerTree, CombinedAssemblerGraph
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

recipes = RecipeList(recipes_file)
assembler_tree = AssemblerTree(item, desired_output_throughput, assembler_crafting_speed, recipes, inputs)

if args.combine_assemblers:
    combined_assembler_tree = CombinedAssemblerGraph(assembler_tree)
    G = combined_assembler_tree.to_graph()
    pos = graphviz_layout(G, prog="dot")
else:
    G = assembler_tree.to_graph()
    pos = graphviz_layout(G, prog="dot") # Dot is good for trees

fig, ax = plt.subplots()
plt.title(f"Asemblers required to achieve {60.0*desired_output_throughput} {item} per minute")

nx.draw_networkx(
    G,
    pos=pos,
    ax=ax,
    arrows=True,
    arrowstyle="-",
    #min_source_margin=30,
    #min_target_margin=30,
    #node_size=2000,
    #node_shape="d",
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
        a.annotate(f"{num_assemblers:.1f}", xy=(32,0), fontsize=10, weight="bold")
    a.annotate(f"{output_throughput:.2f}/s", xy=(64,64), fontsize=10)

    a.axis("off")

plt.show()

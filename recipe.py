from collections import Counter
import pandas as pd
import networkx as nx
from icons import get_icon


def scale_dictionary(d, scale):
    """
    Multiply all the values in dictionary d
    by the scale factor and return the result
    """
    for key in d:
        d[key] *= scale
    return d


def add_dictionaries(d1, d2):
    """
    Merge two dictionaries d1 and d2 and
    add up any common keys
    """
    return dict(Counter(d1) + Counter(d2))


class Recipe:
    """
    Contains information about one item in factorio (e.g.
    iron_plate or production_science_pack), including the
    items that are required to create it, assembling times,
    etc.
    """

    def __init__(self, item_dataframe):
        """

        """
        self.item = item_dataframe.iloc[0]["item"]
        self.num_produced = item_dataframe.iloc[0]["num_produced"]
        self.handcraft_time = item_dataframe.iloc[0]["handcraft_time"]

        # dictionary mapping item name to number required
        self.ingredients = dict(
            zip(item_dataframe["resource"], item_dataframe["quantity"]))

    def __repr__(self):
        """
        Get string representation
        """
        return (
            f"Recipe for {self.num_produced} {self.item} in {self.handcraft_time}s, "
            + f"using {self.ingredients}")

    def assemblers_required(self, throughput, assembler_crafting_speed=1):
        """
        Calculate the number of assemblers required to get throughput items/second
        from this recipe. assembler_crafting_speed is 1 (for human), 0.5 for
        assembly_machine_1, 0.75 for assembly_machine_2, and 1.25 for assembly_machine_3.

        Note: modules change the crafting speed
        """
        return throughput * self.recipe_time(
            assembler_crafting_speed) / self.num_produced

    def recipe_time(self, assembler_crafting_speed):
        """
        Calculate the time taken to run the recipe once. Depends on the
        crafting speed, which is:
        - 1 for human,
        - 0.5 for assembly_machine_1
        - 0.75 for assembly_machine_2
        - 1.25 for assembly_machine_3

        Note: this is not necessarily the time to craft a single item (e.g. copper_cable)
        """
        return self.handcraft_time / assembler_crafting_speed


class RecipeList:
    """
    A list of all the recipes, along with methods for performing common
    operations
    """

    def __init__(self, factorio_resources_ods):
        factorio_resources = pd.read_excel(factorio_resources_ods,
                                           engine="odf")
        self.recipes = {}
        for item, group in factorio_resources.groupby("item"):
            self.recipes[item] = Recipe(group)

    def get_raw_material_counts(self, item, raw_materials):
        """
        Get a dictionary of all the raw materials that are required to make
        the given item, in terms of the raw_materials list.
        """
        item_recipe = self.get_recipe(item)
        all_raw_materials = {}
        for ingredient, num_required in item_recipe.ingredients.items():

            # If self is a raw material, then return the num_required
            if ingredient in raw_materials:
                scaled_ingredient_raw_materials = {ingredient: num_required}
            else:
                ingredient_raw_materials = self.get_raw_material_counts(
                    ingredient, raw_materials)
                scaled_ingredient_raw_materials = scale_dictionary(
                    ingredient_raw_materials, num_required)

            all_raw_materials = add_dictionaries(
                all_raw_materials, scaled_ingredient_raw_materials)

        return scale_dictionary(all_raw_materials,
                                1.0 / item_recipe.num_produced)

    def get_item_dependencies(self, item, raw_materials):
        """
        Get the tree of recipe dependencies for the given item, down to the raw_materials
        specified. Returns a nested dictionary mapping ingredients to lists of their ingredients
        (raw materials map to empty lists)        """
        item_recipe = self.get_recipe(item)
        item_dependencies = {}
        for ingredient in item_recipe.ingredients:

            # If self is a raw material, then it has an empty list of dependencies
            if ingredient in raw_materials:
                item_dependencies[ingredient] = {}
            else:
                item_dependencies[ingredient] = self.get_item_dependencies(
                    ingredient, raw_materials)

        return item_dependencies

    def get_recipe(self, item):
        """
        Get the Recipe corresponding to item. Raises a ValueError if the item
        does not exist
        """
        try:
            return self.recipes[item]
        except:
            raise ValueError(
                f"Item {item} does not exist in the recipes list. Check the resources .ods file."
            )

    def ingredient_assemblers_per_recipe(self, item, assembler_crafting_speed,
                                         raw_materials):
        """
        How many assemblers are required to sustain one assembly machine
        continuously running the recipe to make item. Returns a dictionary
        mapping ingredient names to number of assembly machines.

        Note: the assembler_crafting_speed does not actually matter currently, as
        the same assembler is assumed for the item and the ingredients. Later, could
        generalise to allow different assemblers.
        """
        assembler_counts = {}
        item_recipe = self.get_recipe(item)
        item_recipe_time = item_recipe.recipe_time(assembler_crafting_speed)
        for ingredient, num_required in item_recipe.ingredients.items():
            throughput = num_required / item_recipe_time

            if ingredient in raw_materials:
                # Just ignore the material, from the perspective of assembly machines
                continue

            ingredient_recipe = self.get_recipe(ingredient)
            assembler_counts[
                ingredient] = ingredient_recipe.assemblers_required(
                    throughput, assembler_crafting_speed)
        return assembler_counts


class AssemblerTree:
    """
    This is the tree of assemblers required to generate a particular throughput of
    item production at the top level. It is assumes all assemblers are the same kind.
    It is made from a RecipesList and a top-level item.

    An AssemblerTree has the following attributes:
    - item: the item name that this node makes
    - output_throughput: the number of items per second that this node makes
    - num_assemblers: the number of assemblers required at this node to sustain this throughput
    - ingredients: a list of AssemblerTrees making dependencies of this item

    """

    def __init__(self, item, throughput, assembler_crafting_speed, recipes,
                 raw_materials):
        self.item = item

        # If the item is a raw material, then set the number of assemblers to zero,
        # but still save the output throughput. This corresponds to the raw material
        # source throughput requirement
        self.output_throughput = throughput
        self.ingredients = []
        if item in raw_materials:
            self.num_assemblers = 0
        else:
            item_recipe = recipes.get_recipe(item)
            item_recipe_time = item_recipe.recipe_time(
                assembler_crafting_speed)
            self.num_assemblers = item_recipe.assemblers_required(
                throughput, assembler_crafting_speed)

            # Now go through each ingredient working out its throughput requirement to sustain
            # item production
            for ingredient, num_required in item_recipe.ingredients.items():
                ingredient_output_throughput = self.num_assemblers * num_required / item_recipe_time
                ingredient_assembler_tree = AssemblerTree(
                    ingredient, ingredient_output_throughput,
                    assembler_crafting_speed, recipes, raw_materials)
                self.ingredients.append(ingredient_assembler_tree)

    def is_raw_material(self):
        return len(self.ingredients) == 0

    def total_raw_input_throughput(self):
        """
        Add up all the raw output throughputs over the leaf nodes (with no assembling machines), which
        are interpreted as the required input throughputs of the raw materials
        """
        total_throughput = {}

        if self.is_raw_material():
            return {self.item: self.output_throughput}
        else:
            for ingredient_assembler_tree in self.ingredients:
                total_throughput = add_dictionaries(
                    total_throughput,
                    ingredient_assembler_tree.total_raw_input_throughput())

        return total_throughput

    def to_dict(self):
        return {
            "item": self.item,
            "assemblers": self.num_assemblers,
            "output_throughput": self.output_throughput,
            "ingredients": [i.to_dict() for i in self.ingredients]
        }

    def add_node(self, G):
        """
        Append this object as a node in a networkx graph. Returns
        the index of the node which was just added.
        """
        next_node_index = G.number_of_nodes()
        G.add_node(
            next_node_index,
            item=self.item,
            icon=get_icon(self.item),
            num_assemblers=self.num_assemblers,
            output_throughput=self.output_throughput,
        )
        return next_node_index

    def to_graph(self, G=None):
        """
        Convert the object to a networkx graph.

        The function is recursive. On the way down the tree (which
        is a depth-first order), each ingredient (i.e. assembler node)
        is assigned a number. On the way up, edges are assigned between
        the node numbers. You cannot do this on the way down, because
        you do not know what the node numbers, because the node numbers
        of all the children of the current node are not known yet.
        """

        if G is None:
            G = nx.Graph()

        current_node_index = self.add_node(G)

        # Now iterate over the children adding them
        for ingredient_assembler_tree in self.ingredients:

            F, ingredient_node_index = ingredient_assembler_tree.to_graph(G)
            G = nx.compose(G, F)

            # Now we're going back up the graph, start adding the edges.
            G.add_edge(current_node_index, ingredient_node_index)

        # Only return the ingredient index if not at the top level
        if current_node_index == 0:
            return G
        else:
            return G, current_node_index


class CombinedAssemblerGraph:
    """
    This is the tree of assemblers required to generate a particular throughput of
    item production at the top level, but where resources only appear once in the tree.
    Compared to AssemblerTree, this graph can contain cycles between the same resource
    may be used to make two different items.
    """

    def __init__(self, assembler_tree):

        # A map from strings to a dictionary of node information
        self.nodes = {}

        # A set of edges -- pairs of the form (item_producer, item_consumer)
        self.edges = set()

        self.add_assembler_tree(assembler_tree)

    def push_assembler_node(self, assembler_tree):
        """
        Add an assembler node (assembler_tree) to the nodes list. If there
        is currently no node for this item, create one, give it the next
        free node index, and save the assembler_tree data in it. If there
        is already a node, add in the num_assemblers and output_throughput.
        """
        item = assembler_tree.item
        if item not in self.nodes:
            self.nodes[item] = {
                "num_assemblers": assembler_tree.num_assemblers,
                "output_throughput": assembler_tree.output_throughput
            }
        else:
            self.nodes[item]["num_assemblers"] += assembler_tree.num_assemblers
            self.nodes[item][
                "output_throughput"] += assembler_tree.output_throughput

    def add_assembler_tree(self, assembler_tree):
        """
        Adds the nodes from an assembler tree to self.nodes, and
        adds edges to self.edges
        """

        # Save the assembler_tree as a node
        self.push_assembler_node(assembler_tree)

        for ingredient_assembler_tree in assembler_tree.ingredients:

            # Add edges from all ingredients to the parent node
            self.edges.add(
                (assembler_tree.item, ingredient_assembler_tree.item))

            self.add_assembler_tree(ingredient_assembler_tree)

    def __repr__(self):
        """
        Print the nodes and edges.
        """
        return f"Nodes: {self.nodes}, Edges:{self.edges}"

    def to_graph(self):
        """
        Convert the graph to networkx for plotting
        """
        G = nx.DiGraph()

        # Networkx labels by numbers, but our key is item name.
        # Keep track of it here.
        item_to_node_index = {}

        for item, node in self.nodes.items():
            num_assemblers = node["num_assemblers"]
            output_throughput = node["output_throughput"]
            next_index = len(item_to_node_index)
            item_to_node_index[item] = next_index
            G.add_node(next_index,
                       item=item,
                       icon=get_icon(item),
                       num_assemblers=num_assemblers,
                       output_throughput=output_throughput)

        for (item_1, item_2) in self.edges:
            index_1 = item_to_node_index[item_1]
            index_2 = item_to_node_index[item_2]
            G.add_edge(index_1, index_2)

        return G

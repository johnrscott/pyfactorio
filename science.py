#!/usr/bin/env python

from recipe import RecipeList, AssemblerTree, add_dictionaries, scale_dictionary
from rich import print
from plots import plot_assembler_tree

raw_materials = [
    "steel_plate",
    "iron_plate",
    "copper_plate",
    "coal",
    "stone",
    "stone_brick",
    "petroleum_gas",
    "heavy_oil",
    "water",
    "plastic_bar",
    "sulfur",
    "lubricant",
    "sulfuric_acid"
]

all_science = [
    "automation",
    "logistic",
    "military",
    "chemical",
    "production",
    "utility"
]


desired_science_throughput = 1.0/5 # per second

recipes = RecipeList("factorio_resources.ods")
science_assembler_trees = [AssemblerTree(name + "_science_pack", desired_science_throughput, 0.75, recipes, raw_materials) for name in all_science]
raw_input_throughputs = [tree.total_raw_input_throughput() for tree in science_assembler_trees]
total = {}
for d in raw_input_throughputs:
    total = add_dictionaries(total, d)

total_per_minute = scale_dictionary(total, 60)
    
print(total)

for name in all_science:
    plot_assembler_tree(name + "_science_pack", desired_science_throughput, 0.75, "factorio_resources.ods", raw_materials)


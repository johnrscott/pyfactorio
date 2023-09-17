#!/usr/bin/env python

from recipe import RecipeList, AssemblerTree, add_dictionaries, scale_dictionary
from rich import print
from plots import plot_assembler_tree

from icons import get_icon

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
    "sulfuric_acid",
    "light_oil"
]

desired_throughput = 10.0/60 # per second

recipes = RecipeList("factorio_resources.ods")

plot_assembler_tree("power_armor_mk2", desired_throughput, 0.75, "factorio_resources.ods", raw_materials)


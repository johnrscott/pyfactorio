from recipe import Recipe
from recipe import RecipeList, AssemblerTree
import pytest

raw_materials = [
    "steel_plate",
    "iron_plate",
    "copper_plate",
    "coal",
    "stone",
    "stone_brick",
    "petroleum_gas",
    "heavy_oil",
    "plastic_bar",
    "sulfuric_acid",
    "water",
    "battery",
    "electric_engine_unit"
]

### Test for raw materials

def test_electronic_circuit_raw_material_counts():
    recipes = RecipeList("factorio_recipes.ods")
    counts = recipes.get_raw_material_counts("electronic_circuit", raw_materials)
    assert counts == {"copper_plate": 1.5, "iron_plate": 1}

def test_advanced_circuit_raw_material_counts():
    recipes = RecipeList("factorio_recipes.ods")
    counts = recipes.get_raw_material_counts("advanced_circuit", raw_materials)
    assert counts == {"copper_plate": 5, "iron_plate": 2, "plastic_bar": 2}

def test_processing_unit_raw_material_counts():
    recipes = RecipeList("factorio_recipes.ods")
    counts = recipes.get_raw_material_counts("processing_unit", raw_materials)
    assert counts == {"copper_plate": 40, "iron_plate": 24, "plastic_bar": 4, "sulfuric_acid": 5}

def test_flying_robot_frame_raw_material_counts():
    recipes = RecipeList("factorio_recipes.ods")
    counts = recipes.get_raw_material_counts("flying_robot_frame", raw_materials)
    assert counts == {"copper_plate": 4.5, "iron_plate": 3, "steel_plate": 1,
                      "battery": 2, "electric_engine_unit": 1,}

def test_production_science_raw_material_counts():
    recipes = RecipeList("factorio_recipes.ods")
    counts = recipes.get_raw_material_counts("production_science_pack", raw_materials)
    assert counts == pytest.approx({"copper_plate": 57.5/3, "iron_plate": 32.5/3,
                                    "steel_plate": 25.0/3, "plastic_bar": 20.0/3,
                                    "stone": 15.0/3, "stone_brick": 10.0/3})

### Tests for assemblers required

def test_assemblers_required_for_automation_science_pack():
    recipes = RecipeList("factorio_recipes.ods")
    recipe = recipes.get_recipe("automation_science_pack")
    # Using a human
    assert recipe.assemblers_required(10, 1) == 50
    # Using assembly_machine_1
    assert recipe.assemblers_required(10, 0.5) == 100
    # Using assembly_machine_2
    assert recipe.assemblers_required(10, 0.75) == 200.0/3
    # Using assembly_machine_3
    assert recipe.assemblers_required(10, 1.25) == 40

    
def test_assemblers_required_for_advanced_circuit():
    recipes = RecipeList("factorio_recipes.ods")
    recipe = recipes.get_recipe("advanced_circuit")
    assert recipe.assemblers_required(0.5, 0.5) == 6
    assert recipe.assemblers_required(3, 0.5) == 36
    assert recipe.assemblers_required(1, 0.5) == 12

def test_assemblers_required_for_copper_cable():
    recipes = RecipeList("factorio_recipes.ods")
    recipe = recipes.get_recipe("copper_cable")
    assert recipe.assemblers_required(4, 1) == 1
    assert recipe.assemblers_required(63, 0.75) == 21

### Tests for number of ingredient assemblers
def test_ingredient_assemblers_for_productivity_module():
    recipes = RecipeList("factorio_recipes.ods")
    num_assemblers = recipes.ingredient_assemblers_per_recipe("productivity_module", 1, raw_materials)
    assert num_assemblers == pytest.approx({"electronic_circuit": 5.0/30 ,
                                            "advanced_circuit": 2})

def test_ingredient_assemblers_for_logistic_science_pack():
    recipes = RecipeList("factorio_recipes.ods")
    num_assemblers = recipes.ingredient_assemblers_per_recipe("logistic_science_pack", 0.5, raw_materials)
    assert num_assemblers == pytest.approx({"inserter": 1.0/12, "transport_belt": 1.0/12})

def test_ingredient_assemblers_for_automation_science_pack():
    recipes = RecipeList("factorio_recipes.ods")
    num_assemblers = recipes.ingredient_assemblers_per_recipe("automation_science_pack", 0.5, raw_materials)
    assert num_assemblers == pytest.approx({"iron_gear_wheel": 0.1})

### Test full assembler tree

def test_military_science_pack_assembler_tree():
    recipes = RecipeList("factorio_recipes.ods")
    assembler_tree = AssemblerTree("military_science_pack", 150.0/60, 1.25,
                                   recipes, raw_materials)
    # Taken from the factorio wiki
    expected = {
        'item': 'military_science_pack',
        'assemblers': 10.0,
        'output_throughput': 2.5,
        'ingredients': [
            {
                'item': 'grenade',
                'assemblers': 8.0,
                'output_throughput': 1.25,
                'ingredients': [
                    {'item': 'coal', 'assemblers': 0, 'output_throughput': 12.5,
                     'ingredients': []},
                    {'item': 'iron_plate', 'assemblers': 0,
                     'output_throughput': 6.25, 'ingredients': []}
                ]
            },
            {
                'item': 'piercing_rounds_magazine',
                'assemblers': 3.0,
                'output_throughput': 1.25,
                'ingredients': [
                    {'item': 'copper_plate', 'assemblers': 0, 'output_throughput': 6.25,
                     'ingredients': []},
                    {
                        'item': 'firearm_magazine',
                        'assemblers': 1.0,
                        'output_throughput': 1.25,
                        'ingredients': [{'item': 'iron_plate', 'assemblers': 0,
                                         'output_throughput': 5.0, 'ingredients': []}]
                    },
                    {'item': 'steel_plate', 'assemblers': 0, 'output_throughput': 1.25,
                     'ingredients': []}
                ]
            },
            {'item': 'wall', 'assemblers': 1.0, 'output_throughput': 2.5,
             'ingredients': [{'item': 'stone_brick', 'assemblers': 0,
                              'output_throughput': 12.5, 'ingredients': []}]}
        ]
    }
    assert assembler_tree.to_dict() == expected
    

def test_military_science_pack_total_raw_input_throughput():
    recipes = RecipeList("factorio_recipes.ods")
    assembler_tree = AssemblerTree("military_science_pack", 150.0/60, 1.25,
                                   recipes, raw_materials)
    # Taken from the factorio wiki
    expected = {
        'coal': 12.5,
        'iron_plate': 11.25,
        'copper_plate': 6.25,
        'steel_plate': 1.25,
        'stone_brick': 12.5
    }

    assert assembler_tree.total_raw_input_throughput() == expected
    

    

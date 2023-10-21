# Why the heck are you using python m8
# Speed, have you heard of it?
# What about type safety?
#! /usr/bin/env python3
# vim:fenc=utf-8
#
"""

"""


# checks if the passed item was short and looks up the
# full name, which is required by the rest of the code.
def lookupItemAliases(item):

    # Do not put plurals as the key!
    lookupItemAliasesDict = {
        ('gear'): 'iron_gear_wheel',
        # belts
        ('yellowbelt'): 'transport_belt',
        ('redbelt'): 'fast_transport_belt',
        ('bluebelt'): 'express_transport_belt',
        ('yellowunderground'): 'underground_belt',
        ('redunderground'): 'fast_underground_belt',
        ('blueunderground'): 'express_underground_belt',
        ('yellowsplitter'): 'splitter',
        ('redsplitter'): 'fast_splitter',
        ('bluesplitter'): 'express_splitter',
        #
        ('yellowinserter'): 'inserter',
        ('redinserter'): 'long-handed_inserter',
        ('blueinserter'): 'fast_inserter',
        #
        ('greencircuit'): 'electronic_circuit',
        ('redcircuit'): 'advanced_circuit',
        ('bluecircuit'): 'processing_unit',
        #
        ('assembler'): 'assembling_machine_1',
        ('blueassembler'): 'assembling_machine_2',
        ('yellowassembler', 'green_assemmbler'): 'assembling_machine_3',
        #
        ('plastic'): 'plastic_bar',
        #
        ('redscience'): 'automation_science_pack',
        ('greenscience'): 'logistic_science_pack',
        ('greyscience'): 'military_science_pack',
        ('bluescience'): 'chemical_science_pack',
        ('purplescience'): 'production_science_pack',
        ('yellowscience'): 'utility_science_pack',
        ('whitescience'): 'space_science_pack'
    }

    try:
        # remove underscores and make lowercase
        newItem = item.replace("_", "").lower()
        # if ends in s strip it
        if newItem[-1] == 's':
            newItem = newItem[:-1]
        item = lookupItemAliasesDict[newItem]
    except KeyError:
        item = item
    return item

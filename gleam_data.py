"""Script for importing and visualisain gleam data

"""
import os
import glob
import csv
from xml.etree import ElementTree

import pandas as pd


def get_data_level(directory_name, data_level, ids, compartment_ids, use_cache):
    if use_cache:
        final = pd.read_csv(os.path.join("gleam_results", directory_name, '{}_level_full.csv'.format(data_level)))
    else:
        filepath = os.path.join("gleam_results", directory_name, data_level)
        data_tables = []
        for data_filename in glob.iglob(os.path.join(filepath, "*.tsv")):
            file_ids = os.path.split(data_filename)[1].replace(".tsv", "").split("-")
            data_table = pd.read_csv(data_filename, delimiter= "\t")
            if data_level == 'cities':
                country_var = ids['City Name'].loc[ids['City ID'] == int(file_ids[0])].values
            else:
                country_var = ids['Name'].loc[ids['ID'] == int(file_ids[0])].values
            data_table[data_level] = country_var[0] if len(country_var) == 1 else None
            data_table['compartment'] = compartment_ids[int(file_ids[1])]
            data_tables.append(data_table)
        
        final = pd.concat(data_tables)
        final.to_csv(os.path.join('gleam_results', directory_name, '{}_level_full.csv'.format(data_level)))
    return final

def import_id_tables(simulation, data_level):
    dataset = pd.read_csv("gleam_results/{}/md_{}.tsv".format(simulation, data_level), delimiter= "\t")
    return dataset

def import_gleam_results(simulation_name, data_level, use_cache = False):
    ids = import_id_tables(simulation_name, data_level)
    compartments = get_result_compartments(simulation_name)
    return get_data_level(simulation_name, data_level, ids, compartments, use_cache)
    # Iterate through Cirectory and add in results/


def get_result_compartments(simulation_name):
    et = ElementTree.parse('gleam_results/{}/definition.xml'.format(simulation_name))
    root = et.getroot()
    namespace = root.tag.split("}")[0] + "}"
    definition = root.find("{}definition".format(namespace))
    compartments = definition.find("{}resultCompartments".format(namespace))

    compartments_dict = {}
    for idx, child in enumerate(compartments):
        compartments_dict[idx] = child.text

    return compartments_dict

if __name__ == "__main__":
    simulation_name = "1587933160667.A0B_export" 
    simulation_keys = {
        'initial_practice' : "1587933160667.A0B_export" , 
        'with_exceptions' : "1588632881133.A0B_export"
    }

    dataset = import_gleam_results(simulation_keys['with_exceptions'], "cities", use_cache=False)

    print(dataset.head)

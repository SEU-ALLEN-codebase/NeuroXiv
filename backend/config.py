'''
config file loading function
'''

import json
import os
from pandas import MultiIndex
import itertools
import numpy as np

from pathlib import Path
root_path = str(Path(os.path.abspath(__file__)).parent)
config_folder = os.path.join(root_path,"config")


def get_projplot_ticks():
    '''
    :argument:
        None
    :return:
        celltype_list: list of cell type, for arbor projection plot
        arbor_target_region_list: list of arbor_target_region, for arbor projection plot
    '''
    path = os.path.join(config_folder, "plot.json")
    with open(path, 'r') as f:
        d = json.load(f)
    celltype_list = d["proj_plot"]["celltype_list"]
    arbor_target_region_list = d["proj_plot"]["arbor_target_region_list"]

    return celltype_list, arbor_target_region_list


def get_proj_region():
    '''
    :argument:
        None
    :return:
        list of selected brain regions and layers of projection features
    '''
    path = os.path.join(config_folder, "proj.json")
    with open(path, 'r') as f:
        d = json.load(f)
    regions = d["regions"]
    layers = d["layers"]

    return regions, layers


def get_morpho_feature_name():
    '''
    :argument:
        None
    :return:
        list of name of all morphology features
    '''
    path = os.path.join(config_folder, "morpho.json")
    with open(path, 'r') as f:
        d = json.load(f)
    morpho = d

    return morpho


def get_df_cols():
    '''
    :argument:
        None
    :return:
        list: columns of neurons.neuron_df.
    '''
    basic = ["data_source", "celltype", "brain_atlas", "recon_method", "has_recon_axon", "has_recon_den", "has_ab"]

    mfn = get_morpho_feature_name()
    morpho = ["_".join(["morpho"] + list(np.char.lower(x))) for x in
              itertools.product(["axon", "den"], mfn)]

    regions, layers = get_proj_region()

    proj = ["_".join(["proj"] + list(x)) for x in itertools.product(["axon", "den"], regions + layers, ["rela", "abs"])]

    arbor_proj = ["_".join(["proj_arbor"] + list(x)) for x in
                  itertools.product(regions + layers, ["rela", "abs", "dar"])]

    cols = basic + morpho + proj + arbor_proj

    return cols, {"basic": len(basic), "morpho": len(mfn), "proj": 2 * (len(regions) + len(layers))}


def create_col_path_mapping():
    '''
    create the col_path_mapping.json file, which contains "query_name" and
    a list of how to find its value from neuron.info_dict.
    :return: None
    '''
    cols = get_df_cols()
    a = [["info.json", "Source"], ["info.json", "CellType"], ["info.json", "BrainAtlas"],
         ["info.json", "Reconstruction_Method"], ["info.json", "Reconstruction_Axon"],
         ["info.json", "Reconstruction_Dendrite"], ["info.json", "Has_AutoArbor"]]
    a.extend([list(x) for x in itertools.product(["Feature_Axon.json", "Feature_Dendrite.json"],
                                                 get_morpho_feature_name())])
    regions, layers = get_proj_region()
    a.extend([list(x) for x in itertools.product(["Projection_Axon.json", "Projection_Dendrite.json"],
                                                 regions + layers, ["all"],
                                                 ["Proj_Value_Norm", "Proj_Value"]
                                                 )])
    a.extend([list(x) for x in itertools.product(["Projection_All_Arbor.json"],
                                                 regions + layers, ["all"],
                                                 ["Proj_Value_Norm", "Proj_Value", "Distal_Arbor_Ratio"]
                                                 )])
    with open(config_folder + "/col_path_mapping.json", "w") as f:
        json.dump(dict(zip(cols[0], a)), f, indent=4)

    return


def get_col_path_mapping():
    '''
    read col_path_mapping.json file
    :return:
        dictionary
    '''
    path = os.path.join(config_folder, "col_path_mapping.json")
    with open(path, 'r') as f:
        d = json.load(f)

    return d

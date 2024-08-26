'''
object of data loading
'''

from typing import Iterable, List
import pandas as pd
import os
import json
import numpy as np
import config
import time

# global variable
df_col_path_mapping = config.get_col_path_mapping()


def format_float(x):
    '''
    used for formatted output of the float
    '''
    if type(x) == int:
        return int(x)
    elif x >= 1:
        return float(np.format_float_positional(x, precision=2, unique=True, fractional=True, trim='-'))
    else:
        return float(np.format_float_positional(x, precision=2, unique=True, fractional=False, trim='k'))


class neuron():
    '''
    object of a single neuron reconstruction
    '''

    def __init__(self,
                 neuron_id: str,
                 path: str,
                 relative_path: str
                 ):
        '''
        all object properties should be initialized and explained here
        Arguments:
            neuron_id: string, id of neuron
            path: string, folder containing neuron file 
        '''
        self.id = neuron_id
        self.path = path
        self.relative_path = relative_path
        # load neuron info
        # flag of whether getting info from memory or disk
        self.from_memory = True
        # dictionary of neuron info, key is info name, value is info content
        self.info_dict = {}
        # # data frame of neuron info, each column contains a neuron information
        # self.info_df = pd.DataFrame()
        # list of neuron info, each column contains a neuron information, prepared for each row of neurons.neuron_df
        self.info_df_list = []
        # populate dict and df with content under path
        self._load_info()

    def _load_info(self):
        '''
        load neuron info from neurons.path and populate:
            neuron.info_dict
            neuron.info_df
        Arguments:
        Return:
            True if success 
        '''
        # To-Do
        if self.from_memory:
            self._load_info_from_memory()
            self.info_df_list = self.get_df_info()

        return True

    def _load_info_from_memory(self):
        '''
        load neuron info from neurons.path and populate:
            neuron.info_dict
            neuron.info_df
        :argument:
            None
        :return:
            True if success
        '''
        path_folder = os.path.join(self.path, self.id)
        file_list = os.listdir(path_folder)
        for name in file_list:
            p = os.path.join(path_folder, name)
            # load *.json content to memory
            if name.endswith(".json"):
                with open(p, 'r') as f:
                    self.info_dict[name] = json.load(f)
            # load *.png src to memory
            elif name.endswith(".png"):
                self.info_dict[name] = p.replace(self.path, self.relative_path)

        return True

    def get_df_info(self):
        '''
        from config/col_path_mapping.json get the keys as the elements of neurons.neuron_df.columns,
        and get the value as the hierarchy of the neurons.neuron_df's row value
        :return:
            a list represents a row of neurons.neuron_df
        '''
        if not self.info_dict:
            return

        df_list = [None] * len(df_col_path_mapping)
        for i, item in enumerate(df_col_path_mapping.items()):
            k, v = item  # k like "proj_arbor_IP_rela", v like ["Projection_All_Arbor.json", "IP", "Proj_Value_Norm"]
            tmpd = None
            if v:  # get specific value
                tmpd = self.info_dict
                for infokey in v:
                    tmpd = tmpd.get(infokey)
                    if tmpd is None:
                        break
            df_list[i] = tmpd

        return df_list

    def get_info_from_memory(self):
        '''
        return a dictionary containing all the information of the neuron
        :argument:
            None
        :return:
            True if success
        '''

        all_info_dict = {}
        img_src_list = []
        morpho_info_list = []
        proj_info_list = []

        tmp_dict = self.info_dict.get("info.json")
        if tmp_dict is not None:
            all_info_dict["id"] = "_".join([tmp_dict["Source"], tmp_dict["ID"], tmp_dict["BrainAtlas"]])
            all_info_dict["celltype"] = tmp_dict["CellType"]
            all_info_dict["brain_atlas"] = tmp_dict["BrainAtlas"]

        # img_src
        # temporally no soma and bouton data
        titles = ["brain", "whole neuron", "dendrite", "axon", "soma", "bouton"]
        aliaslists = [["sagittal", "axial", "coronal"], ["top", "side", "front"],
                      ["top", "side", "front"], ["top", "side", "front"],
                      ["top", "side", "front"], ["top", "side", "front"]]
        filelists = [["Img_Brain_Full_XY.png", "Img_Brain_Full_XZ.png", "Img_Brain_Full_YZ.png"],
                     ["Img_Full_XY.png", "Img_Full_XZ.png", "Img_Full_YZ.png"],
                     ["Img_Dendrite_XY.png", "Img_Dendrite_XZ.png", "Img_Dendrite_YZ.png"],
                     ["Img_Axon_XY.png", "Img_Axon_XZ.png", "Img_Axon_YZ.png"],
                     ["Img_Soma_XY.png", "Img_Soma_XZ.png", "Img_Soma_YZ.png"],
                     ["Img_Bouton_XY.png", "Img_Bouton_XZ.png", "Img_Bouton_YZ.png"]]
        for title, aliaslist, filelist in zip(titles, aliaslists, filelists):
            slides = []
            for alias, file in zip(aliaslist, filelist):
                tmp_path = self.info_dict.get(file)
                if tmp_path is not None:
                    slides.append({"view": alias, "src": tmp_path})
            if slides:
                img_src_list.append({"title": title, "slides": slides})
        all_info_dict["img_src"] = img_src_list

        # morpho_info
        aliaslist = ["axon", "dendrite", "dendrite_radius4", "soma", "bouton"]
        filelist = ["Feature_Axon.json", "Feature_Dendrite.json", "Feature_Dendrite_Radius4.json",
                    "Feature_Soma.json", "Feature_Bouton.json"]
        for alias, file in zip(aliaslist, filelist):
            tmp_dict = self.info_dict.get(file)
            if tmp_dict is not None:
                tmp_info_list = [{"metric": x, "value": format_float(tmp_dict.get(x))} for x in tmp_dict.keys()]
                morpho_info_list.append({"type": alias, "info": tmp_info_list})
        all_info_dict["morpho_info"] = morpho_info_list

        # proj_info
        aliaslist = ["axon", "dendrite", "arbor", "soma", "bouton"]
        filelist = ["Projection_Axon.json", "Projection_Dendrite.json", "Projection_All_Arbor.json",
                    "Projection_Soma.json", "Projection_Bouton.json"]
        for alias, file in zip(aliaslist, filelist):
            tmp_dict = self.info_dict.get(file)
            if tmp_dict is not None:
                tmp_info_list = [
                    {"region": x, "relative": format_float(tmp_dict.get(x).get("all").get("Proj_Value_Norm")),
                     "abs": format_float(tmp_dict.get(x).get("all").get("Proj_Value"))} for x in tmp_dict.keys()]
                proj_info_list.append({"type": alias, "info": tmp_info_list})
        all_info_dict["proj_info"] = proj_info_list

        return all_info_dict

    def get_info(self):
        '''
        return a dictionary containing all the information of the neuron
        Arguments:
            None
        Return:
            info: dictionary; check API design of get_neuron_info() for format
        '''
        # To-Do
        all_info_dict = {}
        if self.from_memory:
            all_info_dict = self.get_info_from_memory()
        else:
            self._load_info_from_memory()
            all_info_dict = self.get_info_from_memory()
            # Do I need to free memory of self.info_dict here?

        return all_info_dict


class neurons():
    '''
    object of a single neuron reconstruction
    '''

    def __init__(self,
                 path: str,
                 relative_path: str,
                 max_load: int = -1):
        '''
        all object properties should be initialized and explained here
        Arguments:
            path: string, folder containing all neurons
            relative_path: string, path for generating online dir
            max_load: int, maximum number of neurons load, use a small number for testing
        '''
        self.path = path
        self.relative_path = relative_path
        # load all neurons
        # dictionary of neurons, key is neuron id, value is neuron class
        self.neuron_dict = {}
        # data frame of neurons, each row is a neuron, column contains neuron information
        self.neuron_df = pd.DataFrame()
        # populate dict and df with content under path
        self._load_all_neurons(max_load)

    def _load_all_neurons(self, max_load: int = -1):
        '''
        load all neurons from neurons.path and populate:
            neurons.neuron_dict
            neurons.neuron_df
        Arguments:
        Return:
            count: int; number of neurons loaded
        '''
        # To-Do
        list_folders = os.listdir(self.path)
        df_list = []
        df_list_append = df_list.append
        neuron_id_list = []

        for folder in list_folders:
            neuron_id = folder
            path_folder = self.path
            _neuron = neuron(neuron_id, path_folder, self.relative_path)
            self.neuron_dict[neuron_id] = _neuron
            neuron_id_list.append(neuron_id)
            # info_df_list is not null only when loading from memory,
            # else need load from memory first, then get info_df_list.
            if _neuron.info_df_list:
                df_list_append(_neuron.info_df_list)
            else:
                _neuron._load_info_from_memory()
                df_list_append(_neuron.get_df_info())

            # only for test
            print(len(self.neuron_dict), neuron_id)
            if max_load > 0:
                if len(self.neuron_dict) >= max_load:
                    break

        self.neuron_df = pd.DataFrame(df_list, columns=df_col_path_mapping.keys(), index=neuron_id_list)
        # change reconstruction_* value to 0 or 1,
        for cname in ["has_recon_axon", "has_recon_den", "has_recon_soma", "has_recon_bouton", "has_ab"]:
            if cname not in df_col_path_mapping:
                continue
            tmpdf = self.neuron_df[cname].copy()
            tmpdf[tmpdf > 1] = 1
            self.neuron_df[cname] = tmpdf

        count = len(self.neuron_dict)

        return count

    def get_neuron_info(self, neuron_id: str):
        '''
        return detail information of a single neuron based on neuron id 
        if neuron_id does not exist, return None
        Arguments:
            neuron_id: string; id of neuron to find
        Return:
            info: dictionary; a dictionary containing basic information of all neurons
        check website API doc for more info
        '''
        if neuron_id in self.neuron_dict:
            return self.neuron_dict[neuron_id].get_info()
        else:
            return None

    def get_info_all(self):
        '''
        return basic information of all neurons 
        Arguments:
        Return:
            info: dictionary; containing basic information of all neurons
        check API doc for more info
        '''
        return self.get_info_criteria()

    def get_info_criteria(self, querry_dict: dict = None):
        '''
        Arguments:
            querry_dict: dict of search query
                        {
                            name1: true,                    ----> binary
                            name2: ['VPM','VPL','MOp'],     ----> category
                            name3: [0,4],                   ----> range
                            ...
                        }
        Return:
            info: dictionary; containing basic information of all neurons
        Return formate is the same as get_info_all()
        Return None if no neuron meet the creteria
        Return whole list if querry_dict is set to None
        '''
        if querry_dict is None: querry_dict = {}
        # 1. for each neuron, compare with creteria, skip the neuron if does not meet
        neuron_list = self.search_neuron(querry_dict)
        # 2. conduct statistic analysis of neuron
        neuron_info = self.get_info_list(neuron_list)
        return neuron_info

    def get_info_list(self, neuron_id_list: List[str] = None):
        '''
        return detail information of a list of neurons based on their id
        Arguments:
            neuron_id_list: list of string; ids of neuron to analysis
        Return:
            info: dictionary; containing basic information of neurons in the list
        check API doc of get_info_all() for more info
        return None if list is empty
        '''
        if neuron_id_list is None: neuron_id_list = []
        # To-Do
        if not neuron_id_list:
            return None

        all_info_dict = {}
        basic_info_dict = {"counts": []}
        morpho_info_list = []
        proj_info_list = []
        plot_dict = {'proj_plot': [], 'hist_plot': []}
        neurons_list = []
        neurons_fail_list = []

        morpho_type_dict = {}
        proj_type_dict = {}
        celltype_list, arbor_target_region_list = config.get_projplot_ticks()
        ct_alllen, ct_dislen = {}, {}
        for i in range(len(celltype_list)):
            tmpdict1, tmpdict2 = {}, {}
            for j in range(len(arbor_target_region_list)):
                tmpdict1[arbor_target_region_list[j]], tmpdict2[arbor_target_region_list[j]] = [], []
            ct_alllen[celltype_list[i]], ct_dislen[celltype_list[i]] = tmpdict1, tmpdict2
        neurons_list_values = []  # prepare for basic_info statistic
        for _id in neuron_id_list:
            _neuron = self.neuron_dict.get(_id)
            if _neuron is None:
                neurons_fail_list.append({"id": _id, "msg": "Not found"})
                continue
            _n_info_dict = _neuron.info_dict
            # neurons
            neurons_list.append({
                "id": "_".join([_n_info_dict["info.json"]["Source"], _n_info_dict["info.json"]["ID"],
                                _n_info_dict["info.json"]["BrainAtlas"]]),
                "img_src": _n_info_dict.get("Img_Full_YZ.png"),  # only load whole neuron maximum projection img
                "celltype": _n_info_dict["info.json"]["CellType"],
                "brain_atlas": _n_info_dict["info.json"]["BrainAtlas"],
                "has_dendrite": False if _n_info_dict["info.json"]["Reconstruction_Dendrite"] == 0 else True,
                "has_axon": False if _n_info_dict["info.json"]["Reconstruction_Axon"] == 0 else True,
                "has_soma": False if _n_info_dict["info.json"]["Reconstruction_Soma"] == 0 else True,
                "has_bouton": False if _n_info_dict["info.json"]["Reconstruction_Bouton"] == 0 else True
            })
            neurons_list_values.append(list(neurons_list[-1].values()))  # prepare for basic_info statistic

            # morpho_info
            for k in _n_info_dict.keys():
                if k.startswith("Feature"):
                    if k not in morpho_type_dict:
                        # memory leak !!!
                        # morpho_type_dict[k] = dict(zip(_n_info_dict[k].keys(),
                        #                         [[]]*len(_n_info_dict[k])))
                        morpho_type_dict[k] = {}
                        for tmp_key in _n_info_dict[k].keys():
                            morpho_type_dict[k][tmp_key] = []
                    for sub_k in morpho_type_dict[k]:
                        morpho_type_dict[k][sub_k].append(_n_info_dict[k][sub_k])

            # proj_info
            for k in _n_info_dict.keys():
                if k.startswith("Projection"):
                    if k not in proj_type_dict:
                        proj_type_dict[k] = {}
                        for tmp_key in _n_info_dict[k].keys():
                            proj_type_dict[k][tmp_key] = [[], []]  # [[relative], [abs]]
                    for sub_k in _n_info_dict[k]:  # sub_k is region
                        if sub_k not in proj_type_dict[k]:
                            proj_type_dict[k][sub_k] = [[], []]
                        proj_type_dict[k][sub_k][0].append(_n_info_dict[k][sub_k]["all"]["Proj_Value_Norm"])
                        proj_type_dict[k][sub_k][1].append(_n_info_dict[k][sub_k]["all"]["Proj_Value"])

            # plot: proj_info (arbor projection info)
            if "Projection_All_Arbor.json" in _n_info_dict:
                ap = _n_info_dict["Projection_All_Arbor.json"]
                info = _n_info_dict["info.json"]
                ct = info["CellType"]
                if ct not in celltype_list:
                    continue
                for key in arbor_target_region_list:
                    if key not in ap:
                        alllen, dislen = 0, 0
                    else:
                        alllen = ap[key]["all"]["Proj_Value"]
                        dislen = ap[key]["all"]["Distal_Arbor_Ratio"] * alllen
                    ct_alllen[ct][key].append(alllen)
                    ct_dislen[ct][key].append(dislen)

        if len(neurons_list) == 0:  # all neuron_id in input list cannot be searched return as null input list
            return None
        # morphology feature statistic and plot: hist_plot statistic
        for item in morpho_type_dict.items():
            _type = item[0].replace("Feature_", "").replace(".json", "").lower()
            _info = []
            feature_dict = item[1]
            for sub_item in feature_dict.items():
                _info.append({"metric": sub_item[0], "mean": format_float(np.mean(sub_item[1])), "std": format_float(np.std(sub_item[1]))})
            morpho_info_list.append({"type": _type, "info": _info})
        # projection feature statistic
        for item in proj_type_dict.items():
            _type = item[0].replace("Projection_", "").replace(".json", "").lower()
            _info = []
            proj_dict = item[1]
            sum_abs = 0
            for sub_item in proj_dict.items():
                _abs = np.mean(sub_item[1][1])
                sum_abs += _abs
                _info.append({"region": sub_item[0], "relative": _abs, "abs": format_float(_abs)})
            for i, d in enumerate(_info):
                _info[i]["relative"] = format_float(_info[i]["relative"] / sum_abs)
            proj_info_list.append({"type": _type, "info": _info})
        # plot: proj_plot statistic
        if len(ct_alllen) > 0:
            for i in range(len(celltype_list)):
                ct = celltype_list[i]
                for j in range(len(arbor_target_region_list)):
                    ba = arbor_target_region_list[j]
                    _mean = np.mean(ct_dislen[ct][ba]) if ct_dislen[ct][ba] else 0
                    _ratio = _mean / (np.mean(ct_alllen[ct][ba]) + 1e-7) if _mean != 0 else 0
                    if _mean != 0:
                        plot_dict["proj_plot"].append({
                            "brain_region_id": j,
                            "celltype_id": i,
                            "arbor_length": format_float(_mean),
                            "distal_arbor_ratio": format_float(_ratio)
                        })
        # plot: hist_plot statistic
        # now only use axon, dendrite feature, represent as {"metric": 'axon_Center Shift', ...}
        eps, max_bin_num, ci = 1e-7, 18, 99  # max_bin_num restricts the max bin number is max_bin_num+2
        for item in morpho_type_dict.items():
            _type = item[0].replace("Feature_", "").replace(".json", "").lower()
            if _type not in ["dendrite", "axon"]:
                continue
            feature_dict = item[1]
            for sub_item in feature_dict.items():
                fn = sub_item[0]  # feature name
                vl = np.array(sub_item[1])  # value list
                lb_l, lb_r = np.percentile(vl, [(100 - ci) / 2, 100 - (100 - ci) / 2])
                vl_confidence = vl[(vl > lb_l) & (vl < lb_r)]

                if lb_l == lb_r or len(vl_confidence) <= 1:
                    bin_edges = list(np.histogram_bin_edges(vl))
                    bin_width = bin_edges[1] - bin_edges[0]
                else:
                    bin_edges = list(np.histogram_bin_edges(vl[(vl > lb_l) & (vl < lb_r)]))
                    bin_width = bin_edges[1] - bin_edges[0]
                    bin_edges = [np.min(vl)] + bin_edges + [np.max(vl)]

                if fn in ["Max Branch Order", "Number of Bifurcations"]:  # integer value
                    bin_width = 1 if bin_width < 0.5 else round(bin_width)
                    lb_l, lb_r = np.ceil(lb_l), np.floor(lb_r)
                    bin_edges = [np.min(vl)] + list(np.arange(lb_l, lb_r, bin_width)) + [lb_r] + [np.max(vl)]

                bin_heights = np.histogram(vl, bins=bin_edges)[0]
                bin_heights = bin_heights / np.sum(bin_heights)
                bin_centers = [(bin_edges[xi] + bin_edges[xi + 1]) / 2 for xi in range(len(bin_edges) - 1)]

                plot_dict["hist_plot"].append(
                    {"metric": _type + "_" + fn, "height": list(bin_heights), "center": bin_centers})

        # basic_info statistic
        basic_info_list = []
        n_count = 0
        ccf_count, fmost_count, no_reg = 0, 0, 0
        den_recon, axon_recon, soma_recon, bouton_recon = 0, 0, 0, 0
        ct_dict = {}
        tmp_df = pd.DataFrame(neurons_list_values, columns=neurons_list[0].keys())
        # number counts
        n_count = len(tmp_df)
        # registration atlas counts
        ccf_count = np.sum(tmp_df["brain_atlas"] == "CCFv3")
        fmost_count = np.sum(tmp_df["brain_atlas"] == "fMOST")
        no_reg = n_count - ccf_count - fmost_count
        # reconstruction type counts
        den_recon = np.sum(tmp_df["has_dendrite"] == 1)
        axon_recon = np.sum(tmp_df["has_axon"] == 1)
        soma_recon = np.sum(tmp_df["has_soma"] == 1)
        bouton_recon = np.sum(tmp_df["has_bouton"] == 1)
        # celltype counts
        ct_dict = dict(tmp_df["celltype"].value_counts())

        for name, num in zip(["number of neuron", "CCFv3 registration", "fMOST registration", "no registration",
                              "dendrite reconstruction",
                              "axon reconstruction", "soma reconstruction", "bouton reconstruction"],
                             [n_count, ccf_count, fmost_count, no_reg, den_recon, axon_recon, soma_recon,
                              bouton_recon]):
            if num != 0:
                basic_info_list.append({"name": name, "num": int(num)})

        basic_info_list = basic_info_list + [{"name": "number of " + x[0], "num": int(x[1])} for x in ct_dict.items()]

        basic_info_dict["counts"] = basic_info_list

        # populate and return all_info_dict
        all_info_dict = dict(zip(["basic_info", "morpho_info", "proj_info", "plot", "neurons", "neurons_fail"],
                                 [basic_info_dict, morpho_info_list, proj_info_list, plot_dict, neurons_list,
                                  neurons_fail_list]))

        return all_info_dict

    def search_neuron(self, querry_dict: dict = None):
        '''
        Arguments:
            querry_dict: dict of search query
                        {
                            name1: true,                    ----> binary
                            name2: ['VPM','VPL','MOp'],     ----> category
                            name3: [0,4],                   ----> range
                            ...
                        }
        Return:
            neuron_list: list of string; containing neuron_id of all qualified neurons
        Return [] if no neuron meet the creteria
        Return whole list if both querries are set to None
        '''

        category_querry = []
        range_querry = []
        if querry_dict is None: querry_dict = {}

        # To-Do
        for item in querry_dict.items():
            k, v = item
            if type(v) == list:
                if len(v) == 2:
                    if type(v[0]) != str and type(v[1]) != str:
                        range_querry.append({"name": k, "min": v[0], "max": v[1]})
                        continue
            category_querry.append({"name": k, "values": v if type(v) == list else [v]})

        init_bool = np.array([True] * len(self.neuron_df))

        for d in category_querry:
            name = d.get("name")
            values = d.get("values")
            init_bool = init_bool & self.neuron_df[name].isin(values)

        for d in range_querry:
            name = d.get("name")
            vmin = d.get("min")
            vmax = d.get("max")
            if vmin is not None and vmax is not None:
                init_bool = init_bool & (self.neuron_df[name] >= vmin) & (self.neuron_df[name] <= vmax)
            elif vmin is None and vmax is not None:
                init_bool = init_bool & (self.neuron_df[name] <= vmax)
            elif vmin is not None and vmax is None:
                init_bool = init_bool & (self.neuron_df[name] >= vmin)

        id_list = np.array(self.neuron_df.index)[init_bool].tolist()
        if len(id_list) == 0:
            return []
        else:
            return id_list



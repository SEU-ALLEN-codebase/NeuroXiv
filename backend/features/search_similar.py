from database import DB
import os
import numpy as np
import json
import sys

sys.path.append("..")
from utils import format_float

PATH_ROOT = "D:/NeuroXiv/api"


# PATH_ROOT = ".."


def binary_search(vlist: list, vtarget):
    search_range = 25
    ll = len(vlist)
    vlow, vhigh = vlist[0], vlist[-1]
    if vtarget <= vlow:
        return vlist[0], vlist[search_range]
    elif vtarget >= vhigh:
        return vlist[-search_range], vlist[-1]
    idx = int(round((ll - 1) / 2))
    idxlow, idxhigh = 0, ll - 1
    while True:
        v1, v2 = vlist[idx:idx + 2]
        if v1 <= vtarget <= v2:
            break
        elif vtarget > v2:
            idxlow = idx + 1
        elif vtarget < v1:
            idxhigh = idx
        idx = int(round((idxlow + idxhigh - 1) / 2))

    return vlist[idx - search_range if idx - search_range >= 0 else 0], vlist[
        idx + search_range if idx + search_range < ll else ll - 1]


def Get_Similar_Range(neuron_info):
    morpho_info = neuron_info["morpho_info"]
    onlyAxon = True if len(morpho_info) == 1 and morpho_info[0]["type"] == "axon" else False
    selectedFeatureNames = ["center shift", "average contraction",
                            "max branch order", "max euclidean distance",
                            "slimness", "flatness"]
    f_per = {}
    with open(os.path.join(PATH_ROOT, "config/feature_percentile.json")) as f:
        f_per = json.load(f)

    with open(os.path.join(PATH_ROOT, "config/querry.json")) as f:
        querry = json.load(f)
    q_soma_region = querry["children"][0]["children"][1]
    q_atlas = querry["children"][0]["children"][2]
    qlist = querry["children"][2]["children"][0]["children"] + querry["children"][1]["children"][0]["children"]
    qnamelist = [x['querry_name'] for x in qlist]
    newqlist = []
    if "celltype" in neuron_info.keys():
        q_soma_region["selectedCategory"] = [neuron_info["celltype"]]
        q_soma_region["visible"] = True
        newqlist.append(q_soma_region)
    if "brain_atlas" in neuron_info.keys():
        q_atlas["selectedCategory"] = [neuron_info["brain_atlas"]]
        q_atlas["visible"] = True
        newqlist.append(q_atlas)

    for item1 in morpho_info:
        n_type = item1["type"]
        if not onlyAxon and n_type == "axon":
            continue
        if n_type == "dendrite":  n_type = "den"
        n_info = item1["info"]
        for item2 in n_info:
            if item2["metric"] not in selectedFeatureNames:
                continue
            f_name = "_".join(["morpho", n_type, item2["metric"].replace(" 95ci", "_95ci")])
            f_v = item2["value"]
            qidx = qnamelist.index(f_name)
            interval = f_per[f_name]
            vlow, vhigh = binary_search(interval, f_v)
            qlist[qidx]["visible"] = True
            qlist[qidx]["default_max"] = format_float(vhigh)
            qlist[qidx]["default_min"] = format_float(vlow)
            newqlist.append(qlist[qidx])

    return newqlist


def Count_Distribution():
    '''
    save feature distribution as json file
    '''
    myDB = DB(os.path.join(PATH_ROOT, "database/test_0410.db"))
    df_den = myDB.queryall('''SELECT * FROM Feature_Dendrite''').iloc[:, 1:]
    df_axon = myDB.queryall('''SELECT * FROM Feature_Axon''').iloc[:, 1:]
    pre_dict = {}
    for df in [df_den, df_axon]:
        for col in df.columns:
            series = df[col].values
            interval = np.nanpercentile(series, np.arange(0, 101, 1))
            pre_dict[col] = interval.tolist()
    with open(os.path.join(PATH_ROOT, "config/feature_percentile.json", 'w')) as f:
        json.dump(pre_dict, f, indent=4)


if __name__ == "__main__":
    print()
    # Count_Distribution()
    # print(binary_search([1, 2, 4, 4.4, 23, 45.5, 46], 1.1))
    # from calculate_func import Pipeline
    #
    # print(Get_Similar_Range(Pipeline(r"E:\ZhixiYun\Projects\GitHub\neuron_analysis\tmp\test1\Full.swc")["morpho_info"]))

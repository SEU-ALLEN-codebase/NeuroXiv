'''
object of data loading
'''
import random
import string
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List
import pandas as pd
from daal4py import Any

import config
import time

from database import DB
import itertools
from utils import *
import sqlite3
from LLM import extract_data_final

PATH_ROOT = ""

# global variable
df_col_path_mapping = config.get_col_path_mapping()
myDB = DB(os.path.join(PATH_ROOT, "database/test_0410.db"))

arborColor = [
    [0, 0, 0],
    [225, 0, 0],
    [0, 0, 255],
    [255, 0, 255]
]


def get_summary_info():
    from service import redis_client, get_session_id
    session_id = get_session_id()
    key = f"summary_info:{session_id}"
    return redis_client.hgetall(key)


def get_child_list(celltype):
    # 读取CSV文件
    extracted_data = pd.read_csv("./config/id2celltype.csv")

    # 转换 'child_ids' 列从字符串到整数列表
    extracted_data['children_ids'] = extracted_data['children_ids'].apply(
        lambda x: [int(id_) for id_ in x.strip('[]').split(', ')] if x.strip('[]') else [])

    # 查找指定 celltype 的 child_ids
    try:
        child_ids = extracted_data.loc[extracted_data['acronym'] == celltype, 'children_ids'].iloc[0]
    except IndexError:
        return []  # 如果没有找到指定的 celltype, 返回空列表

    # 将 child_ids 中的每个 id 转换为相应的 acronym
    child_list = []
    for child_id in child_ids:
        acronym = extracted_data.loc[extracted_data['id'] == child_id, 'acronym'].iloc[0]
        child_list.append(acronym)
    return child_list


class neuron:
    '''
    object of a single neuron reconstruction
    '''

    def __init__(self,
                 neuron_id: str,
                 relative_path: str
                 ):
        '''
        all object properties should be initialized and explained here
        Arguments:
            neuron_id: string, id of neuron
            path: string, folder containing neuron file
        '''
        self.id = neuron_id
        self.relative_path = relative_path
        # load neuron info
        # dictionary of neuron info, key is info name, value is info content
        self.info_dict = {}
        # list of neuron info, each column contains a neuron information, prepared for each row of neurons.neuron_df
        self.info_df_list = []

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

    def get_info(self):
        '''
        return a dictionary containing all the information of the neuron
        :argument:
            None
        :return:
            True if success
        '''

        all_info_dict = {}
        morpho_info_list = []
        proj_info_list = []
        conn_info_list = []
        simi_info_list = []
        altas = ""
        vtk_atlas = ''
        hasden, hasaxon, hasapi, haslocal, hasarbor = False, False, False, False, False

        db = DB(os.path.join(PATH_ROOT, "database/test_0410.db"))
        soma_dict = db.queryall('''SELECT * FROM soma WHERE ID == '{}' limit 1;'''.format(self.id))
        db.cur.close()
        soma_pos = []
        soma_pos.append(soma_dict['soma_x'])
        soma_pos.append(soma_dict['soma_y'])
        soma_pos.append(soma_dict['soma_z'])
        all_info_dict['soma'] = soma_pos

        db = DB(os.path.join(PATH_ROOT, "database/test_0410.db"))
        tmp_dict = db.queryall('''SELECT * FROM info WHERE ID == '{}' limit 1;'''.format(self.id))
        tmp_dict['has_recon_axon'] = int(tmp_dict['has_recon_axon'])
        tmp_dict['has_ab'] = int(tmp_dict['has_ab'])
        tmp_dict['has_recon_den'] = int(tmp_dict['has_recon_den'])
        tmp_dict['has_apical'] = int(tmp_dict['has_apical'])
        tmp_dict['has_local'] = int(tmp_dict['has_local'])
        db.cur.close()
        # tmp_dict = myDB.queryall('''SELECT * FROM info WHERE ID == '{}' limit 1;'''.format(self.id))
        if tmp_dict is not None:
            all_info_dict["id"] = self.id
            all_info_dict["celltype"] = tmp_dict["celltype"]
            if tmp_dict["layer"] is not None:
                all_info_dict["layer"] = tmp_dict["layer"]
            all_info_dict["brain_atlas"] = tmp_dict["brain_atlas"]
            all_info_dict["hemisphere"] = tmp_dict["hemisphere"]
            if tmp_dict["brain_atlas"] == 'CCFv3':
                altas = ""
                vtk_atlas = 'vtk'
            else:
                altas = "_ccf-thin"
                vtk_atlas = "vtk_ccf-thin"
            hasden = True if tmp_dict["has_recon_den"] == 1 else False
            hasaxon = True if tmp_dict["has_recon_axon"] == 1 else False
            hasapi = True if tmp_dict["has_apical"] == 1 else False
            haslocal = True if tmp_dict["has_local"] == 1 else False
            hasarbor = True if tmp_dict["has_ab"] == 1 else False

        aliaslist = ["axon", "dendrite"]
        filelist = ["Feature_Axon", "Feature_Dendrite"]
        db = DB(os.path.join(PATH_ROOT, "database/test_0410.db"))
        for alias, file in zip(aliaslist, filelist):
            # tmp_dict = myDB.queryall('''SELECT * FROM {} WHERE ID == '{}' limit 1;'''.format(file, self.id))
            tmp_dict = db.queryall('''SELECT * FROM {} WHERE ID == '{}' limit 1;'''.format(file, self.id))
            if tmp_dict is not None:
                tmp_info_list = [
                    {"metric": " ".join(x.split('_')[2:]) + (
                        " (" + get_feature_unit(x) + ")" if get_feature_unit(x) else ""), "value": format_float(y),
                     "unit": get_feature_unit(x)} for
                    x, y in tmp_dict.items()]
                morpho_info_list.append({"type": alias, "info": tmp_info_list})
        db.cur.close()
        all_info_dict["morpho_info"] = morpho_info_list

        # proj_info
        aliaslist = ["axon", "dendrite", "arbor"]
        filelist = ["Projection_Axon", "Projection_Dendrite", "Projection_All_Arbor"]
        db = DB(os.path.join(PATH_ROOT, "database/test_0410.db"))
        for alias, file in zip(aliaslist, filelist):
            tmp_dict = db.queryall('''SELECT * FROM {} WHERE ID == '{}' limit 1;'''.format(file, self.id))
            if tmp_dict is not None:
                tmp_info_list = []
                items = list(tmp_dict.items())
                for i in range(0, len(tmp_dict), 3 if alias == "arbor" else 2):
                    k_norm, v_norm = items[i]
                    k_abs, v_abs = items[i + 1]
                    if v_norm is not None:
                        region = k_norm.split('_')[-2]
                        tmp_info_list.append({"region": region, "relative": format_float(v_norm),
                                              "abs": format_float(v_abs)})

                tmp_info_list.sort(key=lambda x: x['abs'], reverse=True)
                proj_info_list.append({"type": alias, "info": tmp_info_list})
        db.cur.close()
        all_info_dict["proj_info"] = proj_info_list

        # conn_info
        db = DB(os.path.join(PATH_ROOT, "database/test_0410.db"))
        tmp_dict = db.queryall('''SELECT * FROM conn WHERE ID == '{}' limit 1;'''.format(self.id))
        db.cur.close()
        axon = []
        dendrite = []
        if tmp_dict:
            axon = tmp_dict["axon_ID"]
            dendrite = tmp_dict["dendrite_ID"]
            if axon is not None and axon != "":
                axon = axon.split(",")
                conn_info_list.append({"type": "axon", "num": len(axon), "id_list": axon})
            if dendrite is not None and dendrite != "":
                dendrite = dendrite.split(",")
                conn_info_list.append({"type": "dendrite", "num": len(dendrite), "id_list": dendrite})
        all_info_dict["conn_info"] = conn_info_list

        # simi_info
        db = DB(os.path.join(PATH_ROOT, "database/test_0410.db"))
        tmp_dict = db.queryall('''SELECT * FROM similar WHERE ID == '{}' limit 1;'''.format(self.id))
        db.cur.close()
        # tmp_dict = myDB.queryall('''SELECT * FROM conn WHERE ID == '{}' limit 1;'''.format(self.id))
        proj_simi_list = []
        morpho_simi_list = []
        if tmp_dict:
            proj_simi_list = tmp_dict["Projection Similar Neurons"]
            morpho_simi_list = tmp_dict["Morpho Similar Neurons"]
            if proj_simi_list is not None and proj_simi_list != "":
                proj_simi_list = proj_simi_list.split(",")[:100]
                simi_info_list.append({"type": "projection", "num": len(proj_simi_list), "id_list": proj_simi_list})
            if morpho_simi_list is not None and morpho_simi_list != "":
                morpho_simi_list = morpho_simi_list.split(",")[:100]
                simi_info_list.append(
                    {"type": "morphological", "num": len(morpho_simi_list), "id_list": morpho_simi_list})
        all_info_dict["simi_info"] = simi_info_list
        print(all_info_dict["simi_info"])

        # viewer_info
        dataDir = "/data"
        viewer_info_list = []
        children = []
        dendrite_viewer = {
            "rgb_triplet": [0, 0, 255],
            "id": -1,
            "name": "basal",
            "src": os.path.join(dataDir, self.id, self.id + "_basal.obj"),

            "disabled": not hasden,
        }
        axon_viewer = {
            "rgb_triplet": [255, 0, 0],
            "id": -2,
            "name": "axon",
            "src": os.path.join(dataDir, self.id, self.id + "_axon.obj"),
            "disabled": not hasaxon,
        }

        brain_region_id = brain_name2id([all_info_dict["celltype"]])
        region_viewer = {
            "id": -3,
            "name": "soma region ({})".format(all_info_dict["celltype"]),
            "brain_region_id": brain_region_id,
            "src": os.path.join(dataDir, 'surf', vtk_atlas, all_info_dict["celltype"] + altas + ".vtk"),
            "disabled": False if len(brain_region_id) > 0 else True,
        }
        apical_viewer = {
            "rgb_triplet": [255, 0, 255],
            "id": -4,
            "name": "apical",
            "src": os.path.join(dataDir, self.id, self.id + "_apical.obj"),
            "disabled": not hasapi,
        }
        local_viewer = {
            "rgb_triplet": [0, 0, 255],
            "id": -5,
            "name": "local",
            "src": os.path.join(dataDir, self.id, self.id + "_local.obj"),
            "disabled": not haslocal,
        }

        children.append(dendrite_viewer)
        children.append(axon_viewer)
        children.append(apical_viewer)
        if haslocal:
            children.append(local_viewer)
        children.append(region_viewer)

        directory_path = os.path.join(r'/NeuroXiv/dataset', self.id)
        if not os.path.exists(directory_path):
            return 0

            # 列出目录内容并计数符合条件的文件
        count = 0
        for file in os.listdir(directory_path):
            if 'arbor' in file:
                count += 1
        viewerid = -6
        for i in range(count):
            arbor_viewer = {
                "rgb_triplet": arborColor[i],
                "id": viewerid,
                "name": "arbor" + str(i),
                "src": os.path.join(dataDir, self.id, self.id + "_arbor" + str(i) + ".obj"),
                "disabled": not hasarbor,
            }
            children.append(arbor_viewer)
            viewerid -= 1

        visible_keys = []
        if hasden:
            visible_keys.append(-1)
        if hasaxon:
            visible_keys.append(-2)
        if hasapi:
            visible_keys.append(-4)
        if haslocal:
            visible_keys.append(-5)

        viewer_info_list.append({"id": 0, "name": self.id, "visible_keys": visible_keys,
                                 "children": children})  # arbor传入的是数组
        idcount = 5
        color_map = {
            1: [255, 0, 120],
            2: [0, 120, 255],
            3: [2, 94, 33],
            4: [100, 90, 55]
        }
        for nid, nname, nlist in zip([1, 2, 3, 4], ["axon neighboring neurons", "dendrite neighboring neurons",
                                                    "projection similar neurons", "morphological similar neurons"],
                                     [axon, dendrite, proj_simi_list, morpho_simi_list]):
            tmplist = []
            db = DB(os.path.join(PATH_ROOT, "database/test_0410.db"))
            if nlist is not None:
                for nl in nlist:
                    tmp_dict = db.queryall('''SELECT * FROM info WHERE ID == '{}' limit 1;'''.format(nl))
                    if tmp_dict is None or "celltype" not in tmp_dict.keys():
                        continue
                    # print(tmp_dict)
                    tmp_dict['has_recon_axon'] = int(tmp_dict['has_recon_axon'])
                    tmp_dict['has_ab'] = int(tmp_dict['has_ab'])
                    tmp_dict['has_recon_den'] = int(tmp_dict['has_recon_den'])
                    tmp_dict['has_apical'] = int(tmp_dict['has_apical'])
                    tmp_dict['has_local'] = int(tmp_dict['has_local'])
                    ct = tmp_dict["celltype"]
                    hasden = True if tmp_dict["has_recon_den"] == 1 else False
                    hasaxon = True if tmp_dict["has_recon_axon"] == 1 else False
                    hasapi = True if tmp_dict["has_apical"] == 1 else False
                    haslocal = True if tmp_dict["has_local"] == 1 else False

                    dv = {
                        "rgb_triplet": color_map.get(nid, [0, 0, 0]),
                        "id": idcount + 1,
                        "name": "basal",
                        "src": os.path.join(dataDir, nl, nl + "_basal.obj"),
                        "disabled": not hasden,
                    }
                    ax = {
                        "rgb_triplet": color_map.get(nid, [0, 0, 0]),
                        "id": idcount + 2,
                        "name": "axon",
                        "src": os.path.join(dataDir, nl, nl + "_axon.obj"),
                        "disabled": not hasaxon,
                    }
                    ap = {
                        "rgb_triplet": color_map.get(nid, [0, 0, 0]),
                        "id": idcount + 4,
                        "name": "apical",
                        "src": os.path.join(dataDir, nl, nl + "_apical.obj"),
                        "disabled": not hasapi,
                    }
                    lc = {
                        "rgb_triplet": color_map.get(nid, [0, 0, 0]),
                        "id": idcount + 5,
                        "name": "local",
                        "src": os.path.join(dataDir, nl, nl + "_local.obj"),
                        "disabled": not haslocal,
                    }
                    bri = brain_name2id([ct])
                    rv = {
                        "id": idcount + 3,
                        "name": "soma region ({})".format(ct),
                        "brain_region_id": bri,
                        "src": os.path.join(dataDir, 'surf', vtk_atlas, ct + altas + ".vtk"),
                        "disabled": False if len(bri) > 0 else True,
                    }
                    if 'full' in nl:
                        tmplist.append({"id": idcount, "name": nl, "children": [dv, ax, ap, rv]})
                    else:
                        tmplist.append({"id": idcount, "name": nl, "children": [lc]})
                    idcount += 6
            db.cur.close()
            viewer_info_list.append(
                {"id": nid, "name": nname, "children": tmplist, "disabled": False if len(tmplist) > 0 else True})

        all_info_dict["viewer_info"] = viewer_info_list

        return all_info_dict


class neurons():
    '''
    object of a single neuron reconstruction
    '''

    def __init__(self,
                 relative_path: str):
        '''
        all object properties should be initialized and explained here
        Arguments:
            path: string, folder containing all neurons
            relative_path: string, path for generating online dir
            max_load: int, maximum number of neurons load, use a small number for testing
        '''
        self.relative_path = relative_path
        # load all neurons
        # dictionary of neurons, key is neuron id, value is neuron class
        self.neuron_dict = {}
        self.id_arr = np.array([])
        self.db_item_num = 0
        self.init_neuron_dict()

    def init_neuron_dict(self):
        db = DB(os.path.join(PATH_ROOT, "database/test_0410.db"))
        db.cur.execute('''select ID from info''')
        self.id_arr = np.array(db.cur.fetchall()).flatten()
        self.db_item_num = len(self.id_arr)
        for _id in self.id_arr:
            self.neuron_dict[_id] = neuron(_id, self.relative_path)
        db.cur.close()
        return self.db_item_num

    def get_neuron_info(self, neuron_id: str, atlas: str):
        '''
        return detail information of a single neuron based on neuron id
        if neuron_id does not exist, return None
        Arguments:
            neuron_id: string; id of neuron to find
            atlas: string; atlas of neuron
        Return:
            info: dictionary; a dictionary containing basic information of all neurons
        check website API doc for more info
        '''
        # myDB.cur.execute('''select ID from info where ID like '%{}%' AND brain_atlas = '{}';'''.format(neuron_id,
        # atlas))
        db = DB(os.path.join(PATH_ROOT, "database/test_0410.db"))
        db.cur.execute('''select ID from info where ID like ? AND brain_atlas = ?;''',
                       ("%" + neuron_id + "%", atlas,))
        query_result = db.cur.fetchall()

        db.cur.close()
        df_info = pd.DataFrame(query_result)
        if len(df_info) == 0:
            return None
        neuron_id = df_info.iloc[0, 0]
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
        with open(os.path.join(PATH_ROOT, "config/all_info_web.json")) as f:
            allinfodict = json.load(f)

        return allinfodict

    def get_info_criteria(self, query_dict: dict = None):
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
        if query_dict is None: querry_dict = {}
        # 1. for each neuron, compare with creteria, skip the neuron if does not meet
        t1 = time.time()
        neuron_list = self.search_neuron(query_dict)
        # neuron_list = neuron_list[0:100]
        print("search_neuron_time")
        print("search_neuron_time")
        print(time.time() - t1)
        # 2. conduct statistic analysis of neuron
        t3 = time.time()
        neuron_info = self.get_info_list(neuron_list)
        print("get_info_list_time")
        print(time.time() - t3)
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
        if len(neuron_id_list) == 0:
            return None

        basic_info_dict = {"counts": []}
        morpho_info_list = []
        proj_info_list = []
        plot_dict = {'proj_plot': [], 'hist_plot': []}
        string_neuron_id_list = "','".join(neuron_id_list)
        if len(string_neuron_id_list) != self.db_item_num:
            tmpstr = " WHERE ID IN ( '{}' )".format(string_neuron_id_list)
        else:
            tmpstr = ""
        if len(string_neuron_id_list) != self.db_item_num:
            placeholder = "(" + ",".join("?" for i in neuron_id_list) + ")"
            df_neurons = myDB.queryall(
                '''SELECT ID,data_source,celltype,brain_atlas,has_recon_den,has_recon_axon,has_ab,has_apical,has_local,hemisphere
                FROM info WHERE ID IN ''' + placeholder,
                (*neuron_id_list,))
            df_neurons['has_recon_axon'] = df_neurons['has_recon_axon'].astype(int)
            df_neurons['has_ab'] = df_neurons['has_ab'].astype(int)
            df_neurons['has_recon_den'] = df_neurons['has_recon_den'].astype(int)
            df_neurons['has_apical'] = df_neurons['has_apical'].astype(int)
            df_neurons['has_local'] = df_neurons['has_local'].astype(int)
            df_f_d = myDB.queryall('''SELECT * FROM Feature_Dendrite WHERE ID IN ''' + placeholder, (*neuron_id_list,))
            df_f_a = myDB.queryall('''SELECT * FROM Feature_Axon WHERE ID IN ''' + placeholder, (*neuron_id_list,))
            df_p_d = myDB.queryall('''SELECT * FROM Projection_Dendrite WHERE ID IN ''' + placeholder,
                                   (*neuron_id_list,))
            df_p_a = myDB.queryall('''SELECT * FROM Projection_Axon WHERE ID IN ''' + placeholder, (*neuron_id_list,))
            df_p_aa = myDB.queryall('''SELECT * FROM Projection_All_Arbor WHERE ID IN ''' + placeholder,
                                    (*neuron_id_list,))
        else:
            df_neurons = myDB.queryall(
                '''SELECT ID,data_source,celltype,brain_atlas,has_recon_den,has_recon_axon,has_ab,has_apical,
                has_local FROM info''')
            df_neurons['has_recon_axon'] = df_neurons['has_recon_axon'].astype(int)
            df_neurons['has_ab'] = df_neurons['has_ab'].astype(int)
            df_neurons['has_recon_den'] = df_neurons['has_recon_den'].astype(int)
            df_neurons['has_apical'] = df_neurons['has_apical'].astype(int)
            df_neurons['has_local'] = df_neurons['has_local'].astype(int)
            df_f_d = myDB.queryall('''SELECT * FROM Feature_Dendrite''')
            df_f_a = myDB.queryall('''SELECT * FROM Feature_Axon''')
            df_p_d = myDB.queryall('''SELECT * FROM Projection_Dendrite''')
            df_p_a = myDB.queryall('''SELECT * FROM Projection_Axon''')
            df_p_aa = myDB.queryall('''SELECT * FROM Projection_All_Arbor''')
        t2 = time.time()
        # print("search", t2 - t1)
        # neurons
        df_neurons = df_neurons.set_index('ID', drop=False)
        df_neurons.index.name = None
        exist_all_id_list = list(df_neurons.index)
        exist_id_list = np.intersect1d(neuron_id_list, exist_all_id_list)
        not_exist_id_list = np.setdiff1d(neuron_id_list, exist_all_id_list)
        neurons_fail_list = [{"id": _id, "msg": "Not found"} for _id in not_exist_id_list]
        df_rows = df_neurons.loc[exist_id_list].values
        neurons_list = [{
            "id": _id,
            "data_source": data_source,
            # only load whole neuron maximum projection img
            "img_src": os.path.join(self.relative_path, _id, "Img_Thumbnail_YZ.png"),
            "celltype": ct,
            "brain_atlas": ba,
            "has_dendrite": int(has_d),
            "has_axon": int(has_a),
            "has_apical": int(has_ap),
            "has_arbor": int(has_ab),
            "has_local": 0 if pd.isna(has_lc) else int(has_lc),
            "hemisphere": hemi
        } for _id, data_source, ct, ba, has_d, has_a, has_ab, has_ap, has_lc, hemi in df_rows]
        t3 = time.time()

        # basic_info

        basic_info_list = []
        den_recon, axon_recon, local_recon, soma_recon, bouton_recon = 0, 0, 0, 0, 0

        n_count = len(neuron_id_list)
        ccf_count = int(np.sum(df_neurons["brain_atlas"] == "CCFv3"))
        fmost_count = int(np.sum(df_neurons["brain_atlas"] == "CCF-thin"))
        SEU_count = int(np.sum(df_neurons["ID"].str.contains("SEU-ALLEN")))
        ION_count = int(np.sum(df_neurons["ID"].str.contains("ION")))
        MouseLight_count = int(np.sum(df_neurons["ID"].str.contains("MouseLight")))
        den_recon = int(np.sum(df_neurons["has_recon_den"] == 1)) + int(np.sum(df_neurons["has_local"] == 1))
        apical_recon = int(np.sum(df_neurons["has_apical"] == 1))
        axon_recon = int(np.sum(df_neurons["has_recon_axon"] == 1))
        ct_dict = dict(df_neurons["celltype"].value_counts())

        for name, num in zip(
                ["Total", "SEU-ALLEN", "ION", "MouseLight", "basal dendrite", "apical dendrite", "axon",
                 "soma reconstructions", "bouton reconstructions"],
                [n_count, SEU_count, ION_count, MouseLight_count, den_recon, apical_recon, axon_recon, soma_recon,
                 bouton_recon]):
            if num != 0:
                basic_info_list.append({"name": name, "num": int(num)})

        # basic_info_list.extend([{"name": "number of neurons in " + x[0], "num": int(x[1])} for x in ct_dict.items()])
        basic_info_list.extend([{"name": x[0], "num": int(x[1])} for x in ct_dict.items()])

        basic_info_dict["counts"] = basic_info_list
        t4 = time.time()

        # morpho_info
        eps, ci = 1e-7, 99

        for alias, tmpdf in zip(["dendrite", "axon", "local"], [df_f_d, df_f_a]):
            if len(tmpdf) == 0:
                continue
            if alias == "dendrite":
                tmpdf = tmpdf[np.asarray((df_neurons.loc[tmpdf["ID"]]["has_recon_den"] == 1) | (
                        df_neurons.loc[tmpdf["ID"]]["has_local"] == 1))].dropna(axis=1, how='all').fillna(0)
            elif alias == "axon":
                tmpdf = tmpdf[np.asarray(df_neurons.loc[tmpdf["ID"]]["has_recon_axon"] == 1)].dropna(axis=1,
                                                                                                     how='all').fillna(
                    0)
            tmpdf = tmpdf.iloc[:, 1:]
            dfmean = tmpdf.mean()
            dfstd = tmpdf.std()
            tmpinfo = {"type": alias,
                       "info": [{"metric": " ".join(x.split("_")[2:]) + (
                           " (" + get_feature_unit(x) + ")" if get_feature_unit(x) else ""),
                                 "mean": format_float(dfmean.iloc[i]),
                                 "std": format_float(dfstd.iloc[i]), "unit": get_feature_unit(x)}
                                for i, x in enumerate(dfmean.index)]}
            morpho_info_list.append(tmpinfo)

            # plot: hist_plot
            for col in tmpdf.columns:
                vl = np.array(tmpdf[col])  # value list
                vl = vl[~np.isnan(vl)]
                lb_l, lb_r = np.nanpercentile(vl, [(100 - ci) / 2, 100 - (100 - ci) / 2])
                vl_confidence = vl[(vl > lb_l) & (vl < lb_r)]

                if lb_l == lb_r or len(vl_confidence) <= 1:
                    bin_edges = list(np.histogram_bin_edges(vl, bins="auto"))
                    bin_width = bin_edges[1] - bin_edges[0]
                else:
                    bin_edges = list(np.histogram_bin_edges(vl[(vl > lb_l) & (vl < lb_r)], bins="auto"))
                    bin_width = bin_edges[1] - bin_edges[0]
                    bin_edges = [np.min(vl)] + bin_edges + [np.max(vl)]

                if col.split("_")[-1] in ["max branch order", "number of bifurcations"]:  # integer value
                    bin_width = 1 if bin_width <= 0.5 else round(bin_width)
                    lb_l, lb_r = int(np.ceil(lb_l)), int(np.floor(lb_r))
                    bin_edges = [int(np.min(vl))] + list(np.arange(lb_l, lb_r, bin_width)) + [lb_r] + [int(np.max(vl))]

                bin_heights = np.histogram(vl, bins=bin_edges)[0]
                bin_heights = bin_heights / np.sum(bin_heights)
                bin_centers = [(bin_edges[xi] + bin_edges[xi + 1]) / 2 for xi in range(len(bin_edges) - 1)]

                plot_dict["hist_plot"].append(
                    {"metric": alias + "_" + " ".join(col.split("_")[2:]) + (
                        " (" + get_feature_unit(col) + ")" if get_feature_unit(col) else ""),
                     "height": list(map(lambda x: format_float(x), bin_heights)), "center": bin_centers})

        t5 = time.time()
        # proj_info
        celltype_list, arbor_target_region_list = config.get_projplot_ticks()
        tmpprojplot = []
        tmpprojdf = df_p_aa.copy()
        tmpprojdf["celltype"] = df_neurons["celltype"].loc[tmpprojdf["ID"]].values

        for alias, tmpdf in zip(["dendrite", "axon", "all_arbor"], [df_p_d, df_p_a, df_p_aa]):
            if len(tmpdf) == 0:
                continue
            if alias == "dendrite":
                tmpdf = tmpdf[np.asarray((df_neurons.loc[tmpdf["ID"]]["has_recon_den"] == 1) | (
                        df_neurons.loc[tmpdf["ID"]]["has_local"] == 1))].dropna(axis=1,
                                                                                how='all').fillna(0)
            elif alias == "axon":
                tmpdf = tmpdf[np.asarray(df_neurons.loc[tmpdf["ID"]]["has_recon_axon"] == 1)].dropna(axis=1,
                                                                                                     how='all').fillna(
                    0)
            elif alias == "all_arbor":
                tmpdf = tmpdf[np.asarray(df_neurons.loc[tmpdf["ID"]]["has_ab"] == 1)].dropna(axis=1, how='all').fillna(
                    0)
            cols = tmpdf.columns[1:]
            tmpdf_mean = tmpdf.mean().values

            # tmpdf = tmpdf.iloc[:, 1:].values
            sum_abs = 0 + eps
            tmpinfolist = []
            for i in range(0, len(cols), 3 if alias == "all_arbor" else 2):
                region = cols[i].split("_")[-2]
                _abs = tmpdf_mean[i + 1]
                if _abs is None:
                    continue
                if region not in ['L1', 'L2/3', 'L4', 'L5', 'L6a', 'L6b']:
                    sum_abs += _abs
                tmpinfo = {"region": region, "relative": _abs, "abs": format_float(_abs)}
                tmpinfolist.append(tmpinfo)

            for i, d in enumerate(tmpinfolist):
                tmpinfolist[i]["relative"] = format_float(d["relative"] / sum_abs)
            tmpinfolist.sort(key=lambda x: x['abs'], reverse=True)
            proj_info_list.append({"type": alias, "info": tmpinfolist})

            # plot: proj_plot
            if alias == "all_arbor":
                t8 = time.time()
                proj_plot = []
                proj_plot_append = proj_plot.append
                use_cols = ["celltype"]
                for ba in arbor_target_region_list:
                    use_cols.extend(["proj_arbor_{}_abs".format(ba), "proj_arbor_{}_dar".format(ba)])
                    # use_cols.extend(["proj_axon_{}_abs".format(ba), "proj_axon_{}_rela".format(ba)])
                ctlist = []
                for ct in celltype_list:
                    child = get_child_list(ct)
                    ctlist.extend(child)
                # celltype_list = ctlist
                tmpprojdf = tmpprojdf[use_cols]
                tmpprojdf = tmpprojdf[tmpprojdf["celltype"].isin(ctlist)].fillna(0)

                for a, ct in enumerate(celltype_list):
                    ctlist = get_child_list(ct)
                    ctdf = tmpprojdf[tmpprojdf["celltype"].isin(ctlist)].iloc[:, 1:]
                    ctabsdf_mean = ctdf.mean().values
                    ctdf = ctdf.values
                    celltype_count = len(ctdf)
                    for b, ba in enumerate(arbor_target_region_list):
                        if len(ctdf) == 0:
                            continue
                        else:
                            ctabsdf = ctdf[:, 2 * b]
                            ctdardf = ctdf[:, 2 * b + 1]
                            _mean = ctabsdf_mean[2 * b]
                            _da_mean = np.mean([x * y if not np.isnan(x) else 0 for x, y in zip(ctabsdf, ctdardf)])

                        if _mean != 0:
                            proj_plot_append({
                                "brain_region_id": b,
                                "celltype_id": a,
                                "arbor_length": format_float(_mean),
                                "distal_arbor_ratio": _da_mean,
                                "neuron_count": int(np.sum(ctdf[:, 2 * b] > 0)),
                                "celltype_count": celltype_count
                            })

                t9 = time.time()
                for i, d in enumerate(proj_plot):
                    proj_plot[i]["distal_arbor_ratio"] = format_float(
                        d["distal_arbor_ratio"] / (d["arbor_length"] + eps))
                plot_dict["proj_plot"] = proj_plot
                print("arbor plot1", t9 - t8)

        t6 = time.time()
        all_info_dict = dict(zip(["basic_info", "morpho_info", "proj_info", "plot", "neurons", "neurons_fail"],
                                 [basic_info_dict, morpho_info_list, proj_info_list, plot_dict, neurons_list,
                                  neurons_fail_list]))
        print("neurons", t3 - t2, "basic_info", t4 - t3, "morpho", t5 - t4, "proj", t6 - t5)

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
        binary_querry = []
        range_querry = []
        if querry_dict is None: querry_dict = {}

        # To-Do
        for item in querry_dict.items():
            k, v = item
            if k.find(" ") != -1 or k.find("-") != -1 or k.find("/") != -1:
                k = '"{}"'.format(k)
            if type(v) == list:
                if len(v) == 2:
                    if type(v[0]) != str and type(v[1]) != str:
                        range_querry.append({"name": k, "min": v[0], "max": v[1]})
                        continue
                category_querry.append({"name": k, "values": v})
            elif type(v) == bool:
                if v:
                    binary_querry.append({"name": k, "values": 1})
                else:
                    binary_querry.append({"name": k, "values": 0})

        raw_IDlist = list(myDB.queryall('''SELECT ID FROM info;''')["ID"])

        for d in category_querry:
            name = d.get("name")
            values = d.get("values")
            if name == "celltype":
                child_list = []
                for ct in values:
                    child = get_child_list(ct)
                    child_list.extend(child)
                values.extend(child_list)
                ba = []
                ba_layer = []
                for ct in values:
                    ctsplit = ct.split(" Layer")
                    if len(ctsplit) == 1:
                        ba.append(ct)
                    else:
                        ba_layer.append(tuple(ctsplit[0:2]))

                tmpidlist1 = []
                if ba:
                    tmpidlist1 = list(
                        # myDB.queryall('''SELECT ID FROM info WHERE celltype IN ( '{}' );'''.format("','".join(ba)))[
                        #     "ID"]
                        myDB.queryall(
                            '''SELECT ID FROM info WHERE celltype IN ({});'''.format(",".join("?" for i in ba)),
                            (*ba,))["ID"]
                    )

                raw_IDlist_layer = list(tmpidlist1)  # prepared for brain region search

                for i, (b, l) in enumerate(ba_layer):
                    b = b + l
                    l = "L" + l
                    tmpidlist2 = list(
                        # myDB.queryall('''SELECT ID FROM info WHERE celltype == '{}' and layer == '{}';'''.format(b, l))[
                        #     "ID"]
                        myDB.queryall('''SELECT ID FROM info WHERE celltype == ? and layer == ?;''', (b, l,))[
                            "ID"]
                    )
                    raw_IDlist_layer = np.union1d(raw_IDlist_layer, tmpidlist2)

                if len(raw_IDlist_layer) > 0: raw_IDlist = np.intersect1d(raw_IDlist, raw_IDlist_layer)

            else:
                myDB.cur.execute('''select * from info''')
                valid_names = [tuple[0] for tuple in myDB.cur.description]
                if name not in valid_names:
                    continue
                if not isinstance(values, (tuple, list)):
                    values = [values]
                tmpidlist = list(
                    # myDB.queryall('''SELECT ID FROM info WHERE {} IN ( '{}' );'''.format(name, "','".join(values)))[
                    #     "ID"])
                    myDB.queryall(
                        '''SELECT ID FROM info WHERE {} IN ({});'''.format(name, ",".join("?" for i in values)),
                        values)[
                        "ID"])
                raw_IDlist = np.intersect1d(raw_IDlist, tmpidlist)

        for d in binary_querry:
            name = d.get("name")
            values = d.get("values")
            # tmpidlist = list(
            #     myDB.queryall('''SELECT ID FROM info WHERE {} == {};'''.format(name, values))["ID"])
            myDB.cur.execute('''select * from info''')
            valid_names = [tuple[0] for tuple in myDB.cur.description]
            if name not in valid_names:
                continue
            tmpidlist = list(
                myDB.queryall('''SELECT ID FROM info WHERE {} == ?;'''.format(name), (values,))["ID"])
            raw_IDlist = np.intersect1d(raw_IDlist, tmpidlist)

        for d in range_querry:
            name = d.get("name").replace('"', '')
            vmin = d.get("min")
            vmax = d.get("max")
            tname = None
            namesplit = name.split("_") if name[0] != '"' else name[1:-1].split("_")
            if namesplit[0] == "proj":
                if namesplit[1] == "arbor":
                    tname = "Projection_All_Arbor"
                elif namesplit[1] == "den" or namesplit[1] == "local":
                    tname = "Projection_Dendrite"
                elif namesplit[1] == "axon":
                    tname = "Projection_Axon"
            elif namesplit[0] == "morpho":
                if namesplit[1] == "den" or namesplit[1] == "local":
                    tname = "Feature_Dendrite"
                elif namesplit[1] == "axon":
                    tname = "Feature_Axon"
            else:
                tname = "info"
            if tname is None:
                continue

            myDB.cur.execute('''select * from {}'''.format(tname))
            valid_names = [tuple[0] for tuple in myDB.cur.description]
            if name not in valid_names:
                continue
            if vmin is not None and vmax is not None:
                # tmpidlist = list(myDB.queryall(
                #     '''SELECT ID FROM {} WHERE {} BETWEEN {} AND {};'''.format(tname, name, vmin, vmax))["ID"])
                tmpidlist = list(myDB.queryall(
                    '''SELECT ID FROM {} WHERE [{}] BETWEEN ? AND ?;'''.format(tname, name), (vmin, vmax,))["ID"])
            elif vmin is None and vmax is not None:
                # tmpidlist = list(
                #     myDB.queryall('''SELECT ID FROM {} WHERE {} <= {};'''.format(tname, name, vmax))["ID"])
                tmpidlist = list(
                    myDB.queryall('''SELECT ID FROM {} WHERE {} <= ?;'''.format(tname, name), (vmax,))["ID"])
            # elif vmin is not None and vmax is None:
            else:
                tmpidlist = list(
                    myDB.queryall('''SELECT ID FROM {} WHERE {} >= ?;'''.format(tname, name), (vmin,))["ID"])

            raw_IDlist = np.intersect1d(raw_IDlist, tmpidlist)
        raw_IDlist = list(raw_IDlist)
        if len(raw_IDlist) == 0:
            return []
        else:
            return raw_IDlist

    def inital_data_summary(self, neuron_id_list: List[str] = None):
        print('start extract data')
        neuron_placeholder = "(" + ",".join("?" for _ in neuron_id_list) + ")"
        query_info = f"SELECT ID, data_source, celltype, brain_atlas, has_recon_den, has_recon_axon, has_ab, layer," \
                     f"has_apical, has_local, hemisphere FROM info WHERE ID IN {neuron_placeholder} "
        # Query the database
        query_result = myDB.queryall(query_info, (*neuron_id_list,))
        ana_neus = pd.DataFrame(query_result)
        ana_neus = ana_neus.set_index('ID', drop=False)
        ana_neus.index.name = None
        origin_basic = extract_data_final.global_info_text_v2(ana_neus)

        neuron_placeholder = "(" + ",".join("?" for _ in neuron_id_list) + ")"
        denfeas = myDB.queryall(f"SELECT * FROM Feature_Dendrite WHERE ID IN {neuron_placeholder}", (*neuron_id_list,))
        denfeas = denfeas.set_index('ID', drop=False)
        origin_fea_den = extract_data_final.fea2text_v2(ana_neus, denfeas, axonfea=False)
        axonfeas = myDB.queryall(f"SELECT * FROM Feature_Axon WHERE ID IN {neuron_placeholder}", (*neuron_id_list,))
        axonfeas = axonfeas.set_index('ID', drop=False)
        origin_fea_axon = extract_data_final.fea2text_v2(ana_neus, axonfeas, axonfea=True)

        neuron_placeholder = "(" + ",".join("?" for _ in neuron_id_list) + ")"
        denproj = myDB.queryall(f"SELECT * FROM Projection_Dendrite WHERE ID IN {neuron_placeholder}",
                                (*neuron_id_list,))
        denproj = denproj.set_index('ID', drop=False)
        axonproj = myDB.queryall(f"SELECT * FROM Projection_Axon WHERE ID IN {neuron_placeholder}", (*neuron_id_list,))
        axonproj = axonproj.set_index('ID', drop=False)
        origin_proj_axon = extract_data_final.proj_patterns_v2(ana_neus, axonproj)
        origin_proj_den = extract_data_final.proj_patterns_v2(ana_neus, denproj, axonfea=False)
        return origin_basic, origin_fea_den, origin_fea_axon, origin_proj_den, origin_proj_axon
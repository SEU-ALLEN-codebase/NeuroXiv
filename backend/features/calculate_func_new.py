from scipy.spatial import ConvexHull
from scipy.spatial.distance import cdist
import scipy
import SimpleITK as sitk
import numpy as np
import pandas as pd
import os
import basicfunc
from features import utils_fe
from matplotlib import pyplot as plt
import sys
import matplotlib as mpl
import shutil
from utils import format_float, get_feature_unit

sys.path.append("..")
mpl.use('Agg')


class Neuron():
    '''
    return swc: pandas dataframe
    swc file header: ['id', 'type', 'x', 'y', 'z', 'radius', 'pid']
    eswc file header: ['id', 'type', 'x', 'y', 'z', 'radius', 'pid', 'seg_id', 'level', 'mode', 'timestamp', 'teraflyindex']
    soma: type=1 and pid=-1
    axon arbor : type=2
    dendritic arbor: type = [3,4]
    '''
    SWCHeader = ['id', 'type', 'x', 'y', 'z', 'radius', 'pid']
    ESWCHeader = ['id', 'type', 'x', 'y', 'z', 'radius', 'pid', 'seg_id', 'level', 'mode', 'timestamp', 'teraflyindex']
    NeuriteTypes = ['axon', 'dendrite', 'basal', 'apical']
    NeuColorDict = {'axon': 2, 'dendrite': 3, 'basal': 3, 'apical': 4}

    def __init__(self, path, retype=None, scale=1, sep=' ', from_swc=None, totypes=True, prefind=False):
        self.path = path
        self.swcname = os.path.split(path)[-1]
        if from_swc is None:
            self.df_swc = self.read_swc(self.path, sep=sep)
        else:
            df_swc = pd.DataFrame(from_swc, dtype=np.float32, columns=self.SWCHeader)
            df_swc[["id", "type", "pid"]] = df_swc[["id", "type", "pid"]].astype(np.int32)
            self.df_swc = df_swc.copy()
        if self.swc_checker():
            if scale != 1:
                self.df_swc = self.swc_scale(scale=scale)
            if retype is not None:
                self.df_swc = self.swc_retype(totype=retype)
            self.swc = self.df_swc.values.tolist()
            self.length = len(self.swc)
            if totypes:
                self.neurite_types = self.num_of_neurite_type()
                if self.df_swc[self.df_swc.type == 2].shape[0]:
                    self.df_axon = self.to_neurite_type(mode='axon')
                else:
                    self.df_axon = None
                if self.df_swc[self.df_swc.type == 3].shape[0]:
                    self.df_den = self.to_neurite_type(mode='dendrite')
                else:
                    self.df_den = None
                if self.df_swc[self.df_swc.type == 3].shape[0]:
                    self.df_basal = self.to_neurite_type(mode='basal')
                else:
                    self.df_basal = None
                if self.df_swc[self.df_swc.type == 4].shape[0]:
                    self.df_apical = self.to_neurite_type(mode='apical')
                else:
                    self.df_apical = None
            # self.arbors = [self.to_neurite_type(mode=neutype) for neutype in ['axon', 'basal', 'apical']]
            if prefind:
                self.soma, self.bifurs, self.tips = [], [], []
                if self.length != 0:
                    self.soma = self.df_swc.loc[self.get_soma(), self.SWCHeader].to_list()
                    self.bifurs = self.df_swc[self.df_swc['id'].isin(self.get_bifs())].values.tolist()
                    self.tips = self.df_swc[self.df_swc['id'].isin(self.get_tips())].values.tolist()

    def read_swc(self, file, sep=' ', header=None, skiprows=None):
        if skiprows is None:
            with open(file) as f:
                rows = f.read().splitlines()
            skiprows = 0
            for line in rows:
                if line[0] == "#":
                    skiprows += 1
                    continue
                else:
                    break
        swc = pd.read_csv(file, sep=sep, header=None, skiprows=skiprows)
        if header is None:
            header = self.SWCHeader
            if swc.shape[1] >= 12:
                header = self.ESWCHeader
                for i in np.arange(12, swc.shape[1]):
                    header.append('fea_' + str(i - 12))
        if len(header) == swc.shape[1]:
            swc.columns = header

        return swc

    def save_swc(self, topath, inswc=None, header=None):
        if inswc is None:
            inswc = self.df_swc
        swc = inswc.copy()
        if header is None:
            header = self.SWCHeader
        else:
            for h in header:
                if h not in swc.keys().to_list():
                    header = swc.keys().to_list()
                    break
        # swc.reset_index(inplace=True)
        header[0] = '##' + header[0]
        swc.to_csv(topath, sep=' ', index=0, header=header)
        return True

    def warning_msg(self, msg):
        print("WARNING: file {0} {1}".format(self.path, msg))

    def swc_checker(self):
        # soma checker: only one node with type=1 and parent=-1
        df = self.df_swc.copy()
        if df[(df.type == 1)].shape[0] != 1:
            print('Soma type error')
            return False
        else:
            if df[(df.type == 1) & (df.pid == -1)].shape[0] != 1:
                print('Neuron root error')
                return False
        # type checker: register type 1~4
        if df[(df.type < 1) | (df.type > 4)].shape[0] >= 1:
            print('Neuron type error')
            return False
        # single tree checker
        for p in df['pid']:
            if p > 0 & p not in df['id']:
                print('Error: not a single tree!')
                return False
        # somaid=self.get_soma()
        # # traversal from tip to soma
        # tips = self.get_tips()
        # if len(tips) == 0:
        #     self.warning_msg("No tips in neuron")
        #     return True
        # for tip in tips:
        #     sid = tip
        #     spid = sid
        #     while True:
        #         spid = df.loc[sid, 'pid']
        #         if spid == somaid:
        #             break
        #         if spid not in df.index.to_list():
        #             print('Error: not a single tree!')
        #             return False
        #         sid = spid
        return True

    def to_neurite_type_old(self, inswc=None, mode=None):
        '''
        extract swc arbor :
            all arbors: mode="all", will return a list of swc_arbors order in ['axon','dendrite','basal','apical']
            axon: mode="axon"
            dendrite: mode="dendrite"
            apical dendrite: mode="apical"
            basal dendrite: mode="basal"
        return arbor swc
        '''
        if inswc is None:
            inswc = self.df_swc.copy()
        if mode is None or mode.lower() not in self.NeuriteTypes:
            self.warning_msg("Not a registered mode for neurite type: ['axon','dendrite','basal','apical']")
            return inswc
        target_types = [2, 3, 4]
        if mode.lower() == 'axon':
            target_types = [2]
        elif mode.lower() == 'dendrite':
            target_types = [3, 4]
        elif mode.lower() == 'basal':
            target_types = [3]
        elif mode.lower() == 'apical':
            target_types = [4]
        somaid = self.get_soma(inswc)
        # traversal from tip to soma
        target_tips = self.get_tips(inswc, ntype=target_types)
        if len(target_tips) == 0:
            self.warning_msg("No request arbor of " + mode.lower())
            return inswc
        swc = inswc.copy()
        swc.set_index(['id'], drop=True, inplace=True)
        target_ids = [somaid]
        for tip in target_tips:
            sid = tip
            target_ids.append(sid)
            spid = sid
            while True:
                spid = swc.loc[sid, 'pid']
                if spid == somaid or spid < 0:
                    break
                if spid in swc.index.to_list():
                    if spid not in target_ids:
                        target_ids.append(spid)
                    else:
                        break
                else:
                    self.warning_msg("Not possible")
                    break
                sid = spid
        outswc = inswc[inswc.id.isin(target_ids)].copy()
        return outswc

    def to_neurite_type(self, inswc=None, mode=None):
        '''
        extract swc arbor :
            all arbors: mode="all", will return a list of swc_arbors order in ['axon','dendrite','basal','apical']
            axon: mode="axon"
            dendrite: mode="dendrite"
            apical dendrite: mode="apical"
            basal dendrite: mode="basal"
        return arbor swc
        '''
        if inswc is None:
            inswc = self.df_swc.copy()
        if mode is None or mode.lower() not in self.NeuriteTypes:
            self.warning_msg("Not a registered mode for neurite type: ['axon','dendrite','basal','apical']")
            return inswc
        target_types = [2, 3, 4]
        if mode.lower() == 'axon':
            target_types = [2]
        elif mode.lower() == 'dendrite':
            target_types = [3, 4]
        elif mode.lower() == 'basal':
            target_types = [3]
        elif mode.lower() == 'apical':
            target_types = [4]
        inswc.set_index(['id'], drop=True, inplace=True)
        somaid = self.get_soma(inswc)
        target_ids = inswc[inswc.type.isin(target_types)].index.to_list()
        outswcids = [somaid]
        for nid in target_ids:
            spid = inswc.loc[nid, 'pid']
            if spid not in target_ids:
                sid = nid
                while True:
                    spid = inswc.loc[sid, 'pid']
                    if spid == somaid or spid < 0:
                        break
                    if spid in inswc.index.to_list():
                        if spid not in target_ids:
                            outswcids.append(spid)
                        else:
                            break
                    else:
                        self.warning_msg("Not possible")
                        break
                    sid = spid
        inswc.reset_index(inplace=True)
        outswc = inswc[inswc.id.isin(outswcids + target_ids)].copy()
        return outswc

    def num_of_neurite_type(self, inswc=None):
        if inswc is None:
            inswc = self.df_swc.copy()
        tipids = self.get_tips(inswc)
        tips = inswc[inswc.id.isin(tipids)].copy()
        return tips['type'].value_counts().index.tolist()

    def swc_scale(self, inswc=None, scale=1):
        '''scale the coordinate of swc'''
        if inswc is None:
            inswc = self.df_swc.copy()
        if inswc.shape[0] == 0 or scale == 1:
            return inswc
        inswc['x'] *= np.float16(scale)
        inswc['y'] *= np.float16(scale)
        inswc['z'] *= np.float16(scale)
        return inswc

    def swc_retype(self, inswc=None, totype=2, rid=None):
        '''change type of swc'''
        if inswc is None:
            inswc = self.df_swc.copy()
        if inswc.shape[0] == 0 or totype <= 1:
            return inswc
        if rid is None:
            rid = self.get_soma(inswc)
        inswc['type'] = totype
        inswc.loc[rid, 'type'] = 1
        return inswc

    def get_degree(self, inswc=None):
        '''区分不同类型的node
        internode: degree =2
        tipnode: degree =1
        bifurcation: degree =3
        soma node: degree >=3
        '''
        if inswc is None:
            tswc = self.df_swc.copy()
        else:
            tswc = inswc.copy()
        tswc.set_index(['id'], drop=True, inplace=True)
        tswc['degree'] = tswc['pid'].isin(tswc.index).astype('int')
        # print(tswc['degree'])
        n_child = tswc.pid.value_counts()
        n_child = n_child[n_child.index.isin(tswc.index)]
        tswc.loc[n_child.index, 'degree'] = tswc.loc[n_child.index, 'degree'] + n_child
        return tswc

    def get_soma(self, inswc=None):
        '''return index of soma node in df_swc'''
        if inswc is None:
            df = self.df_swc.copy()
        else:
            df = inswc.copy()
        df_soma = df[(df["type"] == 1) & (df["pid"] == -1)].copy()
        if df_soma.shape[0] == 0:
            df_soma = df[df["pid"] == -1].copy()
            if df_soma.shape[0] == 0:
                self.warning_msg("No soma (type=1) detected...try to find root(pid=-1)")
                self.warning_msg("No soma detected...")
                return None
        if df_soma.shape[0] > 1:
            self.warning_msg("multiple soma detected.")
            return None
        # return df_soma.values[0].tolist()
        return df_soma.index[0]

    def get_keypoints(self, inswc=None, rid=None):
        '''
        Key points: soma,bifurcations,tips
        return idlist
        '''
        if inswc is None:
            swc = self.df_swc.copy()
        else:
            swc = inswc.copy()
        if rid is None:
            rid = self.get_soma(inswc)
        # print(swc.shape)
        swc = self.get_degree(swc)
        idlist = swc[((swc.degree != 2) | (swc.index == rid))].index.tolist()
        return idlist

    def get_tips(self, inswc=None, ntype=None):
        if inswc is None:
            swc = self.df_swc.copy()
        else:
            swc = inswc.copy()
        if swc.shape[0] == 0:
            return None
        swc = self.get_degree(swc)
        if ntype is not None:
            idlist = swc[(swc.degree < 2) & (swc.type.isin(ntype))].index.tolist()
        else:
            idlist = swc[(swc.degree < 2)].index.tolist()
        return idlist

    def get_bifs(self, inswc=None, rid=None, ntype=None):
        if inswc is None:
            swc = self.df_swc.copy()
        else:
            swc = inswc.copy()
        if rid is None:
            rid = self.get_soma(swc)
        # print(swc.shape)
        swc = self.get_degree(swc)
        if ntype is not None:
            idlist = swc[((swc.degree > 2) & (swc.index != rid) & (swc.type == ntype))].index.tolist()
        else:
            idlist = swc[((swc.degree > 2) & (swc.index != rid))].index.tolist()
        return idlist

    def swc2branches(self, inswc=None):
        '''
        reture branch list of a swc
        branch: down to top
        '''
        if inswc is None:
            inswc = self.df_swc.copy()
        keyids = self.get_keypoints(inswc)
        branches = []
        for key in keyids:
            if inswc.loc[key, 'pid'] < 0 | inswc.loc[key, 'type'] <= 1:
                continue
            branch = []
            branch.append(key)
            pkey = inswc.loc[key, 'pid']
            while True:
                branch.append(pkey)
                if pkey in keyids:
                    break
                key = pkey
                pkey = inswc.loc[key, 'pid']
            branches.append(branch)
        return branches


def alignment(neuron: Neuron):
    n = utils_fe.Neuron()
    n.load_eswc(neuron.swc)
    n.normalize_neuron(ntype=list(set(n.ntype)), dir_order='zyx')
    nn = n.convert_to_swclist()
    return Neuron(path=neuron.path, from_swc=nn, totypes=False, prefind=True)


def draw_neuron_thumbnail(swc, save_path=""):
    if len(swc) <= 1:
        return False
    soma = basicfunc.get_soma(swc)
    linelist = basicfunc.generate_linelist(swc)
    ratio = 1
    for orient in ["YZ"]:
        if orient == "XY":
            x1, x2 = 2, 3
        elif orient == "YZ":
            x1, x2 = 3, 4
        elif orient == "XZ":
            x1, x2 = 2, 4
        canvas_w1 = np.max(np.array(swc)[:, x1])
        canvas_h1 = np.max(np.array(swc)[:, x2])
        canvas_w2 = np.min(np.array(swc)[:, x1])
        canvas_h2 = np.min(np.array(swc)[:, x2])

        max_pos = np.max([canvas_w1 - canvas_w2, canvas_h1 - canvas_h2]) / 2

        min_pos = -max_pos

        plt.figure(figsize=(1, 1))
        #         plt.axes().set_aspect('equal', adjustable='datalim')
        plt.axis('square')
        for line in linelist:
            if line[0, 1] == 2:
                color = "red"
                pline = plt.plot(line[:, x1] * ratio, line[:, x2] * ratio, c=color, lw=0.3 * ratio)
                pline[0].set_zorder(0)
            elif line[0, 1] == 4:
                color = "mediumvioletred"
                pline = plt.plot(line[:, x1] * ratio, line[:, x2] * ratio, c=color, lw=0.3 * ratio)
                pline[0].set_zorder(1)
            else:
                color = "dodgerblue"
                pline = plt.plot(line[:, x1] * ratio, line[:, x2] * ratio, c=color, lw=0.3 * ratio)
                pline[0].set_zorder(2)

        pdot = plt.scatter(soma[x1], soma[x2], c='black', s=1 * ratio)
        pdot.set_zorder(3)
        # plt.ylim(canvas_h2 * ratio, canvas_h1 * ratio)
        # plt.xlim(min_pos * ratio, max_pos * ratio)
        xlimmax = max(abs(2 * canvas_w2 / (canvas_w1 - canvas_w2) * max_pos * ratio),
                      abs(2 * canvas_w1 / (canvas_w1 - canvas_w2) * max_pos * ratio))
        plt.ylim(2 * canvas_h2 / (canvas_h1 - canvas_h2) * max_pos * ratio,
                 2 * canvas_h1 / (canvas_h1 - canvas_h2) * max_pos * ratio)
        plt.xlim(-xlimmax, xlimmax)

        plt.axis("off")

        plt.savefig(os.path.join(save_path, "Img_Thumbnail_YZ.png"), bbox_inches='tight', pad_inches=0.01,
                    facecolor="white", dpi=300)
        plt.close()

    return True


def genObj(swcraw, ntype=None, scale=1.0, output_p='./tmp/tmp.obj'):
    swc = []
    if ntype is None:
        swc = list(swcraw)
        pass
    else:
        for node in swcraw:
            if node[1] in ntype:
                swc.append(node)
    objLines = []
    NeuronHash = {}
    for i in range(0, len(swc)):
        NeuronHash[swc[i][0]] = i
        line = 'v ' + str(swc[i][2] * scale) + ' ' + str(swc[i][3] * scale) + ' ' + str(swc[i][4] * scale) + '\n'
        objLines.append(line)
    for i in range(0, len(swc)):
        p = swc[i][6]
        if p not in NeuronHash.keys():
            continue
        line = 'l ' + str(i + 1) + ' ' + str(NeuronHash[p] + 1) + '\n'
        objLines.append(line)

    with open(output_p, 'w') as f:
        f.writelines(objLines)


class SWC_Features():
    '''
    some new features. (see feature_name)
    (swc need resample step=10!!!)
    '''

    def __init__(self, neuron: Neuron, swc_reg=None):
        self.neuron = neuron
        self.feature_name = ["Center Shift", "Relative Center Shift",
                             "Average Contraction", "Average Bifurcation Angle Remote",
                             "Average Bifurcation Angle Local",
                             "Max Branch Order", "Number of Bifurcations", "Total Length",
                             "Max Euclidean Distance", "Max Path Distance", "Average Euclidean Distance",
                             "25% Euclidean Distance",
                             "50% Euclidean Distance", "75% Euclidean Distance", "Average Path Distance",
                             "25% Path Distance",
                             "50% Path Distance", "75% Path Distance",
                             '2D Density', '3D Density',
                             'Area', 'Volume', 'Width', 'Width_95ci', 'Height', 'Height_95ci', 'Depth', 'Depth_95ci',
                             'Slimness', 'Slimness_95ci', 'Flatness', 'Flatness_95ci']
        self.feature_dict = {}
        for fn in self.feature_name:
            self.feature_dict[fn] = None

        if self.neuron.length == 0:
            return

        self.swc = neuron.swc
        self.path = neuron.path
        self.soma = self.neuron.soma
        self.tips = self.neuron.tips
        self.swc_reg = swc_reg
        # self.bifurs = get_bifurs(swc)

        self.calc_feature()

    def calc_feature(self):
        # self.Euc_Dis(self.swc)
        self.Pat_Dis_xuan(self.swc)
        self.center_shift(self.swc)
        if self.feature_dict["Max Euclidean Distance"] is None:
            self.feature_dict["Relative Center Shift"] = None
        else:
            self.feature_dict["Relative Center Shift"] = self.feature_dict["Center Shift"] / self.feature_dict[
                "Max Euclidean Distance"]
        self.size_related_features(self.swc)
        self.xyz_approximate(self.swc)
        self.feature_dict["Number of Bifurcations"] = len(self.neuron.bifurs)

    def Euc_Dis(self, swc):
        dislist = cdist(np.array([self.soma[2:5]]), np.array(swc)[:, 2:5])[0]
        if len(dislist) == 0:
            return [None] * 5
        euc_dis_ave = np.mean(dislist)
        euc_dis_max = np.max(dislist)
        euc_dis_25, euc_dis_50, euc_dis_75 = np.percentile(dislist, [25, 50, 75])

        self.feature_dict["Max Euclidean Distance"] = euc_dis_max
        self.feature_dict["Average Euclidean Distance"] = euc_dis_ave
        self.feature_dict["25% Euclidean Distance"] = euc_dis_25
        self.feature_dict["50% Euclidean Distance"] = euc_dis_50
        self.feature_dict["75% Euclidean Distance"] = euc_dis_75

        return

    def Pat_Dis_xuan(self, swc):
        NT = utils_fe.NeuronTree()
        NT.readSwc_fromlist(swc)
        NT.computeFeature()
        pathdislist = NT.pathTotal
        euxdislist = NT.euxTotal
        length = len(pathdislist)
        if len(pathdislist) == 0 or len(euxdislist) == 0:
            return [None] * 5
        path_dis_ave = np.mean(pathdislist)
        path_dis_max = np.max(pathdislist)
        path_dis_25, path_dis_50, path_dis_75 = np.percentile(pathdislist, [25, 50, 75])

        euc_dis_ave = np.mean(euxdislist)
        euc_dis_25, euc_dis_50, euc_dis_75 = np.percentile(euxdislist, [25, 50, 75])

        self.feature_dict["Max Path Distance"] = path_dis_max
        self.feature_dict["Average Path Distance"] = path_dis_ave
        self.feature_dict["25% Path Distance"] = path_dis_25
        self.feature_dict["50% Path Distance"] = path_dis_50
        self.feature_dict["75% Path Distance"] = path_dis_75
        self.feature_dict["Total Length"] = NT.Length
        self.feature_dict["Average Contraction"] = NT.Contraction
        self.feature_dict["Average Bifurcation Angle Remote"] = NT.BifA_remote
        self.feature_dict["Average Bifurcation Angle Local"] = NT.BifA_local
        self.feature_dict["Max Branch Order"] = NT.Max_Order
        self.feature_dict["Max Euclidean Distance"] = NT.Max_Eux
        self.feature_dict["Average Euclidean Distance"] = euc_dis_ave
        self.feature_dict["25% Euclidean Distance"] = euc_dis_25
        self.feature_dict["50% Euclidean Distance"] = euc_dis_50
        self.feature_dict["75% Euclidean Distance"] = euc_dis_75

    def Pat_Dis(self, swc):
        patlist = []
        soma = self.soma
        id_pathdist = {}
        idlist = np.array(swc)[:, 0].tolist()
        pidlist = np.array(swc)[:, 6].tolist()
        if soma[0] not in pidlist:
            # 此时说明没有连接到soma的通路，寻找最接近soma的root
            maxdist = 1000000
            for node in swc:
                if node == self.soma:
                    continue
                if node[6] not in idlist:
                    cur_dist = np.linalg.norm(np.array(self.soma[2:5]) - np.array(node[2:5]), ord=2)
                    if cur_dist < maxdist:
                        maxdist = cur_dist
                        soma = node

        if self.tips:
            nodes = self.tips
        else:
            nodes = swc
        for node in nodes:
            if node == soma or node == self.soma:
                continue
            cur_node = node
            cur_pathdist = 0
            passbynode = {}
            while True:
                pid = cur_node[6]
                if pid not in idlist:
                    break
                idx = idlist.index(pid)
                new_node = swc[idx]
                delta_pathdist = np.linalg.norm(np.array(cur_node[2:5]) - np.array(new_node[2:5]), ord=2)
                cur_pathdist += delta_pathdist
                if passbynode.keys():
                    passbynode = dict(
                        zip(list(passbynode.keys()), (np.array(list(passbynode.values())) + delta_pathdist).tolist()))
                if new_node == soma:
                    id_pathdist[node[0]] = cur_pathdist
                    id_pathdist.update(passbynode)
                    break
                elif new_node[0] in id_pathdist.keys():
                    id_pathdist[node[0]] = cur_pathdist + id_pathdist[new_node[0]]
                    if passbynode.keys():
                        passbynode = dict(
                            zip(list(passbynode.keys()),
                                (np.array(list(passbynode.values())) + id_pathdist[new_node[0]]).tolist()))
                    id_pathdist.update(passbynode)
                    break
                else:
                    cur_node = new_node
                    passbynode[new_node[0]] = 0

        pathdislist = list(id_pathdist.values())
        length = len(pathdislist)
        if length == 0:
            return [None] * 5
        path_dis_ave = np.mean(pathdislist)
        path_dis_max = np.max(pathdislist)
        path_dis_25, path_dis_50, path_dis_75 = np.percentile(pathdislist, [25, 50, 75])

        self.feature_dict["Max Path Distance"] = path_dis_max
        self.feature_dict["Average Path Distance"] = path_dis_ave
        self.feature_dict["25% Path Distance"] = path_dis_25
        self.feature_dict["50% Path Distance"] = path_dis_50
        self.feature_dict["75% Path Distance"] = path_dis_75

        return

    def center_shift(self, swc):
        soma = self.soma
        swc_ar = np.array(swc)
        centroid = np.mean(swc_ar[:, 2:5], axis=0)
        self.feature_dict["Center Shift"] = np.linalg.norm(np.array(soma[2:5]) - centroid[0:3], ord=2)
        return

    def pixel_voxel_calc(self, swc_xyz):
        swcxyz = np.array(swc_xyz)
        x = np.round(swcxyz[:, 0])
        y = np.round(swcxyz[:, 1])
        z = np.round(swcxyz[:, 2])
        pixels = list(set(list(zip(z, y))))  # 投射到zy平面算pixel z是主方向 且去除了冗余pixel
        voxels = list(set(list(zip(x, y, z))))
        num_pixels = len(pixels)
        num_voxels = len(voxels)

        return num_pixels, num_voxels

    def size_related_features(self, swc):
        num_nodes = len(swc)
        if num_nodes <= 3:
            return [None] * 4
        swc_zy = np.array(swc)[:, 3:5]
        swc_xyz = np.array(swc)[:, 2:5]

        try:
            CH2D = ConvexHull(swc_zy)
            CH3D = ConvexHull(swc_xyz)
        except scipy.spatial.qhull.QhullError:
            return [None] * 4
        # CH2D.area  # 2D情况下这个是周长×
        # CH2D.volume  # 2D情况下这个是面积√
        # CH3D.area    # 3D情况下这个是表面积×
        # CH3D.volume  # 3D情况下这个是体积√
        area = CH2D.volume
        volume = CH3D.volume
        # interpolation of swc so that each pixel/voxel can be occupied on all pathway
        swc_xyz_new = list(swc_xyz)
        swc_arr = np.array(swc)
        idlist = list(swc_arr[:, 0])
        for node in swc:
            pid = node[6]
            x1, y1, z1 = node[2:5]
            if pid not in idlist:
                continue
            else:
                cur_id = idlist.index(pid)
                x2, y2, z2 = swc_xyz[cur_id]
                count = int(np.linalg.norm([x1 - x2, y1 - y2, z1 - z2]) // 1)
                if count != 0:
                    tmp = [[x1 + 1 * x, y1 + 1 * x, z1 + 1 * x] for x in
                           range(1, count + 1)]
                    swc_xyz_new.extend(tmp)

        num_pixels, num_voxels = self.pixel_voxel_calc(swc_xyz_new)
        density_2d = num_pixels / area
        density_3d = num_voxels / volume
        self.feature_dict["Area"] = area
        self.feature_dict["Volume"] = volume
        self.feature_dict["2D Density"] = density_2d
        self.feature_dict["3D Density"] = density_3d

        return

    def xyz_approximate(self, swc):
        '''
        shape related
        :param swc:
        :return:
        '''
        if not swc:
            return [None] * 10
        swcxyz = np.array(swc)[:, 2:5]
        x = swcxyz[:, 0]
        y = swcxyz[:, 1]
        z = swcxyz[:, 2]
        width = np.max(y) - np.min(y)  # y  zyx-registration   height=z-z' width=y-y' depth=x-x'
        height = np.max(z) - np.min(z)  # z
        depth = np.max(x) - np.min(x)  # x
        # confidence interval 95%
        width_95ci = abs(np.percentile(y, 97.5) - np.percentile(y, 2.5))
        height_95ci = abs(np.percentile(z, 97.5) - np.percentile(z, 2.5))
        depth_95ci = abs(np.percentile(x, 97.5) - np.percentile(x, 2.5))

        slimness = width / height  # slimness = width/height
        flatness = height / depth  # flatness = height/depth
        slimness_95ci = width_95ci / height_95ci
        flatness_95ci = height_95ci / depth_95ci

        self.feature_dict["Width"] = width
        self.feature_dict["Height"] = height
        self.feature_dict["Depth"] = depth
        self.feature_dict["Width_95ci"] = width_95ci
        self.feature_dict["Height_95ci"] = height_95ci
        self.feature_dict["Depth_95ci"] = depth_95ci
        self.feature_dict["Slimness"] = slimness
        self.feature_dict["Flatness"] = flatness
        self.feature_dict["Slimness_95ci"] = slimness_95ci
        self.feature_dict["Flatness_95ci"] = flatness_95ci

        return


def feature_extraction(neu, anno, fea_outpath=None, proj_outpath=None):
    proj_dict_neurite = basicfunc.calc_projection(neu.swc, anno=anno)
    neu_align = alignment(neu)
    neu_align_fea = SWC_Features(neu_align)
    neurite_name = neu.path.split('/')[-1]
    # neu_align_fea, proj_dict_neurite = feature_extraction(neu_df,anno)
    bv_neurite = list(neu_align_fea.feature_dict.values())
    neurite_fea_df = pd.DataFrame([bv_neurite], index=[neurite_name], columns=list(neu_align_fea.feature_dict.keys()))
    neurite_fea_df.index.name = 'ID'
    if fea_outpath is not None:
        neurite_fea_df.to_csv(fea_outpath)
    neurite_proj_df = pd.DataFrame(proj_dict_neurite, index=[neurite_name], columns=list(proj_dict_neurite.keys()))
    neurite_proj_df.index.name = 'ID'
    if proj_outpath is not None:
        neurite_proj_df.to_csv(proj_outpath)
    return neurite_fea_df, neurite_proj_df


# def process_file_figs(filepath, topath,resample_step=100,atlas_name='CCFv3',atlas_anno="testdata/annotation_25.nrrd"):
#     '''
#     0. input neuron with standard swc format
#     1. read swc to dataframe
#     2. check soma, type, single tree,...
#     3. resample,rescale
#     4. neurite split
#     5. generate thumbnail
#     6. generate obj files
#     7. feature extraction
#     8. projection extraction
#     '''
#     filename = os.path.split(filepath)[-1]
#     if not os.path.exists(filepath):
#         return False
#     neu_dir_name = f'{filename.replace(".swc", "")}_{atlas_name}'
#     if not os.path.exists(topath):
#         basicfunc.makedir(topath)
#     savewebfolder = os.path.join(topath, neu_dir_name)
#     if not os.path.exists(savewebfolder):
#         basicfunc.makedir(savewebfolder)
#     # copy undownsampled/raw swc into output dir
#     if not os.path.exists(os.path.join(savewebfolder, neu_dir_name+".swc")):
#         shutil.copy(filepath, os.path.join(savewebfolder, neu_dir_name+".swc"))
#     # filepath: for generation of thumbnail fig
#     # neu_df_raw = Neuron(filepath, scale=1)
#     neu=utils_fe.NeuronTree()
#     neu.readSwc(filepath)
#     resamped_neu=neu.resample(step=resample_step)
#     neuswc=[]
#     for s in resamped_neu.NeuronList:
#         neuswc.append([s.n, s.type, s.x, s.y, s.z, s.r, s.parent])
#     neu_df=Neuron(path=filepath,from_swc=neuswc)
#     if not os.path.exists(os.path.join(savewebfolder, "Img_Thumbnail_YZ.png")):
#         aligned_swc = alignment(neu_df)
#         draw_neuron_thumbnail(aligned_swc.swc, savewebfolder)
#     # for the generation of arbors
#     if neu_df.df_axon is not None:
#         output_name = os.path.join(savewebfolder, neu_dir_name + '_axon.obj')
#         if not os.path.exists(output_name):
#             genObj(neu_df.df_axon.values.tolist(), scale=0.04, output_p=output_name)
#     if neu_df.df_basal is not None:
#         output_name = os.path.join(savewebfolder, neu_dir_name + '_basal.obj')
#         if not os.path.exists(output_name):
#             genObj(neu_df.df_basal.values.tolist(), scale=0.04, output_p=output_name)
#     if neu_df.df_apical is not None:
#         output_name = os.path.join(savewebfolder, neu_dir_name + '_apical.obj')
#         if not os.path.exists(output_name):
#             genObj(neu_df.df_apical.values.tolist(), scale=0.04, output_p=output_name)
#     print("Finished generation of related files", filename)
#     # feature extraction
#     neu_df = Neuron(filepath, scale=1,prefind=False)
#     annotmp = sitk.GetArrayFromImage(sitk.ReadImage(atlas_anno))
#     anno = np.transpose(annotmp, axes=[2, 1, 0])
#     if neu_df.df_axon is not None:
#         fea_outpath = os.path.join(savewebfolder, neu_dir_name + '_axon_features.csv')
#         proj_outpath = os.path.join(savewebfolder, neu_dir_name + '_axon_projection.csv')
#         axon_df=Neuron(neu_df.path,from_swc=neu_df.df_axon.values.tolist(),totypes=False)
#         feature_extraction(axon_df,anno,fea_outpath,proj_outpath)
#     if neu_df.df_den is not None:
#         fea_outpath = os.path.join(savewebfolder, neu_dir_name + '_den_features.csv')
#         proj_outpath = os.path.join(savewebfolder, neu_dir_name + '_den_projection.csv')
#         den_df=Neuron(neu_df.path,from_swc=neu_df.df_den.values.tolist(),totypes=False)
#         feature_extraction(den_df,anno,fea_outpath,proj_outpath)
#     return True

def process_file_figs(filepath, topath=r"D:/NeuroXiv/dataset/temp/", resample_step=100, atlas_name='CCFv3'):
    '''
    0. input neuron with standard swc format
    1. read swc to dataframe
    2. check soma, type, single tree,...
    3. resample,rescale
    4. neurite split
    5. generate thumbnail
    6. generate obj files
    7. feature extraction
    8. projection extraction
    '''
    filename = os.path.split(filepath)[-1]
    if not os.path.exists(filepath):
        return False
    neu_dir_name = f'{filename.replace(".swc", "")}_{atlas_name}'
    if not os.path.exists(topath):
        basicfunc.makedir(topath)
    # savewebfolder = os.path.join(topath, neu_dir_name)
    savewebfolder = os.path.split(filepath)[0]
    print(savewebfolder)
    relative_path = savewebfolder.replace("D:/NeuroXiv/dataset", "/data")
    print(relative_path)
    if not os.path.exists(savewebfolder):
        basicfunc.makedir(savewebfolder)
    # copy undownsampled/raw swc into output dir
    if not os.path.exists(os.path.join(savewebfolder, neu_dir_name + ".swc")):
        shutil.copy(filepath, os.path.join(savewebfolder, neu_dir_name + ".swc"))
    # filepath: for generation of thumbnail fig
    # neu_df_raw = Neuron(filepath, scale=1)
    neu = utils_fe.NeuronTree()
    neu.readSwc(filepath)
    resamped_neu = neu.resample(step=resample_step)
    neuswc = []
    for s in resamped_neu.NeuronList:
        neuswc.append([s.n, s.type, s.x, s.y, s.z, s.r, s.parent])
    neu_df = Neuron(path=filepath, from_swc=neuswc)
    if not os.path.exists(os.path.join(savewebfolder, "Img_Thumbnail_YZ.png")):
        aligned_swc = alignment(neu_df)
        draw_neuron_thumbnail(aligned_swc.swc, savewebfolder)

    axon_df = Neuron(neu_df.path, from_swc=neu_df.df_axon.values.tolist(), totypes=False)
    neu_align_axon = alignment(axon_df)
    neu_align_axon_fea = SWC_Features(neu_align_axon)

    den_df = Neuron(neu_df.path, from_swc=neu_df.df_den.values.tolist(), totypes=False)
    neu_align_den = alignment(den_df)
    neu_align_den_fea = SWC_Features(neu_align_den)

    # swc_id = '_'.join(os.path.split(folder_path)[-1].split('_')[:-1])
    info_dict = {"id": filename, "soma": neu_df.df_swc.loc[neu_df.get_soma(), neu_df.SWCHeader].to_list()[2:5]}
    img_src_list = []
    titles = ["whole neuron", "dendrite", "axon"]
    aliaslists = [["top", "side", "front"],
                  ["top", "side", "front"], ["top", "side", "front"]]
    figlists = [["Img_Full_XY.png", "Img_Full_XZ.png", "Img_Full_YZ.png"],
                ["Img_Dendrite_XY.png", "Img_Dendrite_XZ.png", "Img_Dendrite_YZ.png"],
                ["Img_Axon_XY.png", "Img_Axon_XZ.png", "Img_Axon_YZ.png"]]
    for title, aliaslist, figname in zip(titles, aliaslists, figlists):
        slides = []
        for alias, fig in zip(aliaslist, figname):
            slides.append({"view": alias, "src": os.path.join(relative_path, fig)})
        img_src_list.append({"title": title, "slides": slides})

    info_dict["img_src"] = img_src_list

    morpho_info_list = []
    aliaslist = ["axon", "dendrite"]
    fe_list = [neu_align_axon_fea.feature_dict, neu_align_den_fea.feature_dict]
    for alias, fe_dict in zip(aliaslist, fe_list):
        tmp_info_list = [
            {"metric": x.lower().replace("_95ci", " 95ci"), "value": format_float(y),
             "unit": get_feature_unit(x.lower())} for
            x, y in fe_dict.items()]
        morpho_info_list.append({"type": alias, "info": tmp_info_list})

    info_dict["morpho_info"] = morpho_info_list

    # for the generation of arbors
    if neu_df.df_axon is not None:
        output_name = os.path.join(savewebfolder, neu_dir_name + '_axon.obj')
        if not os.path.exists(output_name):
            genObj(neu_df.df_axon.values.tolist(), scale=0.04, output_p=output_name)
    if neu_df.df_basal is not None:
        output_name = os.path.join(savewebfolder, neu_dir_name + '_basal.obj')
        if not os.path.exists(output_name):
            genObj(neu_df.df_basal.values.tolist(), scale=0.04, output_p=output_name)
    if neu_df.df_apical is not None:
        output_name = os.path.join(savewebfolder, neu_dir_name + '_apical.obj')
        if not os.path.exists(output_name):
            genObj(neu_df.df_apical.values.tolist(), scale=0.04, output_p=output_name)

    print("Finished generation of related files", filename)

    hasden = len(neu_df.df_axon) > 1
    hasaxon = len(neu_df.df_basal) > 1

    viewer_info_list = []
    dendrite_viewer = {
        "rgb_triplet": [0, 0, 255],
        "id": -1,
        "name": "basal",
        "src": os.path.join(relative_path,  neu_dir_name + '_basal.obj'),
        "disabled": not hasden,
    }
    axon_viewer = {
        "rgb_triplet": [255, 0, 0],
        "id": -2,
        "name": "axon",
        "src": os.path.join(relative_path,  neu_dir_name + '_axon.obj'),
        "disabled": not hasaxon,
    }
    visible_keys = []
    if hasden:
        visible_keys.append(-1)
    if hasaxon:
        visible_keys.append(-2)

    viewer_info_list.append({"id": 0, "name":  neu_dir_name, "visible_keys": visible_keys,
                             "children": [dendrite_viewer, axon_viewer]})
    info_dict["viewer_info"] = viewer_info_list
    print(info_dict)

    return info_dict

    # feature extraction
    # neu_df = Neuron(filepath, scale=1,prefind=False)
    # annotmp = sitk.GetArrayFromImage(sitk.ReadImage(atlas_anno))
    # anno = np.transpose(annotmp, axes=[2, 1, 0])
    # if neu_df.df_axon is not None:
    #     fea_outpath = os.path.join(savewebfolder, neu_dir_name + '_axon_features.csv')
    #     proj_outpath = os.path.join(savewebfolder, neu_dir_name + '_axon_projection.csv')
    #     axon_df=Neuron(neu_df.path,from_swc=neu_df.df_axon.values.tolist(),totypes=False)
    #     feature_extraction(axon_df,anno,fea_outpath,proj_outpath)
    # if neu_df.df_den is not None:
    #     fea_outpath = os.path.join(savewebfolder, neu_dir_name + '_den_features.csv')
    #     proj_outpath = os.path.join(savewebfolder, neu_dir_name + '_den_projection.csv')
    #     den_df=Neuron(neu_df.path,from_swc=neu_df.df_den.values.tolist(),totypes=False)
    #     feature_extraction(den_df,anno,fea_outpath,proj_outpath)
    # return True


if __name__ == "__main__":
    swc_raw = 'shengdian/182724_2238_x7096_y20268.swc'  # 1um
    # swc_neu = Neuron(swc_raw, scale=1)
    process_file_figs(swc_raw, topath='./testdata', atlas_name='CCFv3')

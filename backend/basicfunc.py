import numpy as np
import pandas as pd
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
from matplotlib import pyplot as plt
import os
from libtiff import TIFF
import re
from scipy.spatial import ConvexHull
import json
import vtk
import SimpleITK as sitk
import alphashape


def read_swc(path, mode="t", scale=None, comments=False):
    '''

    :param path:文件路径
    :param mode: "a"--Axon  "t"--total(all of it)  "d"--Dendrite
    :return: a list like [
                          [id type x y z radius pid],
                          [id type x y z radius pid],
                          ...
                          [id type x y z radius pid],
                                                     ]
    '''
    swc_matrix = []
    comments_list = []
    with open(path) as f:
        while True:
            linelist = []
            line = f.readline()
            if not line:
                break
            if line[0] == "#" or line[0] == 'i' or line[0] == "\n":
                comments_list.append(line)
                continue
            if line.count("\t") >= line.count(" "):
                str_split = "\t"
            elif line.count("\t") <= line.count(" "):
                str_split = " "
            elem = line.strip("\n").strip(" ").split(str_split)
            if mode == "t" or mode == 'T':
                pass
            elif mode == "a" or mode == "A":  # 1s 2a 3d
                if elem[1] not in ['1', '2']:
                    continue
            elif mode == "d" or mode == "D":
                if elem[1] not in ['1', '3', '4']:
                    continue
            for i in range(len(elem)):
                if i == 0 or i == 1 or i == 6:
                    linelist.append(int(elem[i]))
                elif i in [2, 3, 4]:
                    if scale is not None:
                        linelist.append(float(elem[i]) * scale)
                    else:
                        linelist.append(float(elem[i]))
                else:
                    linelist.append(float(elem[i]))

            swc_matrix.append(linelist)

    if mode == 'bifur':
        bifur_matrix = []
        for i in range(len(swc_matrix)):
            count = 0
            for j in range(len(swc_matrix)):
                if swc_matrix[i][0] == swc_matrix[j][6]:
                    count += 1
                if count >= 2:
                    bifur_matrix.append(swc_matrix[i])
                    break
        return bifur_matrix

    if comments:
        return swc_matrix, comments_list
    else:
        return swc_matrix


def get_distances(X, model, mode='l2'):
    '''
    救命恩人https://stackoverflow.com/questions/26851553/sklearn-agglomerative-clustering-linkage-matrix
    :param X:
    :param model:
    :param mode:
    :return:
    '''
    distances = []
    weights = []
    children = model.children_
    dims = (X.shape[1], 1)
    distCache = {}
    weightCache = {}
    for childs in children:
        c1 = X[childs[0]].reshape(dims)
        c2 = X[childs[1]].reshape(dims)
        c1Dist = 0
        c1W = 1
        c2Dist = 0
        c2W = 1
        if childs[0] in distCache.keys():
            c1Dist = distCache[childs[0]]
            c1W = weightCache[childs[0]]
        if childs[1] in distCache.keys():
            c2Dist = distCache[childs[1]]
            c2W = weightCache[childs[1]]
        d = np.linalg.norm(c1 - c2)
        cc = ((c1W * c1) + (c2W * c2)) / (c1W + c2W)

        X = np.vstack((X, cc.T))

        newChild_id = X.shape[0] - 1

        # How to deal with a higher level cluster merge with lower distance:
        if mode == 'l2':  # Increase the higher level cluster size suing an l2 norm
            added_dist = (c1Dist ** 2 + c2Dist ** 2) ** 0.5
            dNew = (d ** 2 + added_dist ** 2) ** 0.5
        elif mode == 'max':  # If the previous clusters had higher distance, use that one
            dNew = max(d, c1Dist, c2Dist)
        elif mode == 'actual':  # Plot the actual distance.
            dNew = d

        wNew = (c1W + c2W)
        distCache[newChild_id] = dNew
        weightCache[newChild_id] = wNew

        distances.append(dNew)
        weights.append(wNew)
    return distances, weights


def Euc_calc(x, y, z, xx, yy, zz):
    '''
    计算(x,y,z) (xx,yy,zz)的欧氏距离
    :param x:
    :param y:
    :param z:
    :param xx:
    :param yy:
    :param zz:
    :return:
    '''
    return np.sqrt((x - xx) ** 2 + (y - yy) ** 2 + (z - zz) ** 2)


def get_soma(swc):
    '''
    获取soma点
    :param swc: read_swc函数的返回值
    :return:[id type x y z radius pid]
    '''
    soma = []
    for i in range(len(swc)):
        if swc[i][1] == 1 and swc[i][6] == -1:
            soma = swc[i]
            break
    if len(soma) == 0:
        for i in range(len(swc)):
            if swc[i][6] == -1:
                soma = swc[i]
    if len(soma) == 0:
        for i in range(len(swc)):
            if swc[i][1] == 1:
                soma = swc[i]
    if len(soma) == 0:
        print("no soma detected...")
    return soma


def get_bifurs(swc):
    '''
    获取bifurcation点
    :param swc: read_swc函数的返回值
    :return:
    '''
    soma = get_soma(swc)
    if not soma:
        return []
    bifur_nodes = []
    df = pd.DataFrame(swc)
    df_vc = df.iloc[:, 6].value_counts()
    for i in range(len(df_vc.index)):
        if df_vc.iloc[i] == 2 and df_vc.index[i] != soma[0] and df_vc.index[i] != -1:
            try:
                idx = np.array(swc)[:, 0].tolist().index((df_vc.index[i]))
            except:
                continue
            bifur_nodes.append(swc[idx])

    return bifur_nodes


def get_tips(swc):
    tips = []
    swc = np.asarray(swc)
    tips = swc[np.in1d(swc[:, 0], np.setdiff1d(swc[:, 0], swc[:, 6]))].tolist()
    # for i in range(swc.shape[0]):
    #     if swc[i][0] not in swc[:, 6].tolist():
    #         tips.append(swc[i].tolist())
    return tips


def sort_swc_index(src):
    dst = []
    NeuronHash = {}
    indexChildren = []
    for i in range(len(src)):
        NeuronHash[src[i][0]] = i
        indexChildren.append([])
    for i in range(len(src)):
        pid = src[i][6]
        idx = NeuronHash.get(pid)
        if idx is None: continue
        indexChildren[idx].append(i)

    LUT_n2newn = {}
    count = 1

    # DBS
    root = get_soma(src)
    root_xyz = np.array(root[2:5])
    root_n = root[0]
    root_idx = NeuronHash[root_n]

    LUT_n2newn[root_n] = count
    tmpnode = list(root)
    tmpnode[0] = count
    count += 1
    dst.append(tmpnode)

    bifurs = indexChildren[root_idx]
    while bifurs:
        cur_node_idx = bifurs.pop()
        LUT_n2newn[src[cur_node_idx][0]] = count
        tmpnode = list(src[cur_node_idx])
        tmpnode[0] = count
        count += 1
        dst.append(tmpnode)
        # print(cur_node_idx)
        cur_node_child_idx = indexChildren[cur_node_idx]
        # one child
        while len(cur_node_child_idx) == 1:
            next_node_idx = cur_node_child_idx[0]
            cur_node_idx = next_node_idx
            LUT_n2newn[src[cur_node_idx][0]] = count
            tmpnode = list(src[cur_node_idx])
            tmpnode[0] = count
            count += 1
            dst.append(tmpnode)

            cur_node_child_idx = indexChildren[cur_node_idx]

        # two children or no children
        if len(cur_node_child_idx) > 1 or len(cur_node_child_idx) == 0:
            bifurs.extend(cur_node_child_idx)

    for i in range(len(dst)):
        node = dst[i]
        mapped_pid = LUT_n2newn.get(node[6])
        if mapped_pid is None:
            mapped_pid = -1
        dst[i][6] = mapped_pid

    return dst


def makedir(fp):
    if not os.path.exists(fp):
        os.makedirs(fp)


def sholl_analysis(swc, step, max_n=None) -> dict:
    def fill_res_dict(res: dict, node1, node2, ):
        node1_pos = np.asarray(node1)[2:5]
        node2_pos = np.asarray(node2)[2:5]
        root_pos = np.asarray(root)[2:5]

        soma_dist1 = np.linalg.norm(root_pos - node1_pos)
        soma_dist2 = np.linalg.norm(root_pos - node2_pos)

        for i in np.arange(soma_dist1 // step + 1, soma_dist2 // step + 1, 1):
            if i not in res: res[i] = 0  # initialization
            res[i] += 1

    # result dict initialization
    res = {}
    if max_n is not None:
        for i in range(1, max_n + 1):
            res[i] = 0
    # else:
    #     for i in range(1, 100000 + 1):
    #         res[i] = 0

    NeuronHash = {}
    indexChildren = []
    for i in range(len(swc)):
        NeuronHash[swc[i][0]] = i
        indexChildren.append([])
    for i in range(len(swc)):
        pid = swc[i][6]
        idx = NeuronHash.get(pid)
        if idx is None: continue
        indexChildren[idx].append(i)

    # DBS
    root = get_soma(swc)
    if len(root) == 0: return res
    root_n = root[0]
    root_idx = NeuronHash[root_n]

    bifurs_chs = indexChildren[root_idx]
    cur_idx = root_idx
    cur_node = root
    while bifurs_chs:
        next_idx = bifurs_chs.pop()
        next_node = swc[next_idx]
        cur_idx = NeuronHash[next_node[6]]
        cur_node = swc[cur_idx]

        fill_res_dict(res, cur_node, next_node)

        cur_idx = next_idx
        cur_node = next_node
        cur_child_idx_list = indexChildren[cur_idx]

        while len(cur_child_idx_list) == 1:
            next_idx = cur_child_idx_list[0]
            next_node = swc[next_idx]
            fill_res_dict(res, cur_node, next_node)

            cur_idx = next_idx
            cur_node = next_node
            cur_child_idx_list = indexChildren[cur_idx]

        if len(cur_child_idx_list) > 1:
            bifurs_chs.extend(cur_child_idx_list)
        elif len(cur_child_idx_list) == 0:
            continue

    return res


def generate_linelist(swc):
    bifur_nodes = get_bifurs(swc)
    bifur_nodes.append(get_soma(swc))
    tips = get_tips(swc)
    linelist = []
    linelist_append = linelist.append
    findedlist = []
    swc = np.asarray(swc)
    idlist = swc[:, 0].tolist()
    bifur_nodes_idlist = np.array(bifur_nodes)[:, 0]

    for i, tempnode in enumerate(tips):
        templist = []
        templist_append = templist.append
        templist_append(tempnode)
        while True:
            if tempnode[6] in idlist:
                idx = idlist.index(tempnode[6])
            else:
                break
            tempnode = swc[idx]
            templist_append(tempnode)

            _id = tempnode[0]

            if not findedlist:
                if _id in bifur_nodes_idlist:
                    findedlist.append(tempnode)
                continue

            if _id in bifur_nodes_idlist:
                if not findedlist:
                    findedlist.append(tempnode)
                else:
                    findedlist_idlist = np.array(findedlist)[:, 0]
                    if _id not in findedlist_idlist:
                        findedlist.append(tempnode)
                    else:
                        break
            else:
                continue
        # print(i+1, "/", len(tips))

        linelist_append(np.array(templist))

    return linelist


def ConcatDiffCols(df1, col1, label1, df2, col2, label2, *args):
    df = pd.DataFrame()
    tmpdf1 = df1[df1[col1].isin(label1)]
    tmpdf1 = tmpdf1.rename(columns={col1: "label"})
    tmpdf2 = df2[df2[col2].isin(label2)]
    tmpdf2 = tmpdf2.rename(columns={col2: "label"})

    df = pd.concat([tmpdf1, tmpdf2])
    if len(args) != 0:
        for i in range(len(args)):
            argdf = args[i][0]
            argcol = args[i][1]
            arglabel = args[i][2]
            argtmpdf = argdf[argdf[argcol].isin(arglabel)]
            argtmpdf = argtmpdf.rename(columns={argcol: "label"})
            df = pd.concat([df, argtmpdf])
    return df


def Get4fw(mt, ci="4fw"):
    arr = np.array(mt)
    xx1 = []
    xx2 = []
    xmean = []
    for i in range(arr.shape[1]):
        mean = np.mean(arr[:, i])
        arrs = np.sort(arr[:, i])
        if ci == "4fw":
            x1, x2 = arrs[int(np.round(len(arrs) / 4))], arrs[int(np.round(len(arrs) * 3 / 4))]
            if len(arrs) % 2 == 1:
                xm = arrs[int(np.round(len(arrs) * 1 / 2))]
            else:
                xm = 0.5 * (arrs[int(len(arrs) * 1 / 2 - 0.5)] + arrs[int(len(arrs) * 1 / 2 + 0.5)])
            xx1.append(x1)
            xx2.append(x2)
            xmean.append(xm)
        elif ci == 95:
            x1, x2 = np.percentile(arrs, 2.5), np.percentile(arrs, 97.5)
            xx1.append(x1)
            xx2.append(x2)
            xmean.append(mean)
    return xx1, xmean, xx2


def Reindex(df, strtype):
    newidx = []
    if strtype != "":
        for i in df.index:
            newidx.append(i.split(".")[0].split(strtype)[-1])
    else:
        for i in df.index:
            newidx.append(i.split(".")[0])
    df.index = newidx


# 雷达图
def radar_factory(num_vars, frame='circle'):
    """
    Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle', 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels, ):
            self.set_thetagrids(np.degrees(theta), labels, )

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def save_swc(path, swc, comments='', eswc=False):
    '''
    save swc file
    :param path:save path
    :param swc:swc list
    :param comments:some remarks in line 2 in swc file
    :return:none
    '''
    if not path.endswith(".swc"):
        path += ".swc"
    with open(path, 'w') as f:
        f.writelines('#' + comments + "\n")
        f.writelines("#n,type,x,y,z,radius,parent\n")
        for node in swc:
            string = ""
            for i in range(len(node)):
                item = node[i]
                if i in [0, 1, 6]:
                    item = int(item)
                elif i in [2, 3, 4]:
                    item = np.round(item, 3)
                string = string + str(item) + " "
                if not eswc:
                    if i == 6:
                        break
            string = string.strip(" ")
            string += "\n"
            f.writelines(string)


def nodes_to_soma(nodes, swc):
    soma = get_soma(swc)
    idlist = np.array(swc)[:, 0].tolist()
    waylists = []
    for node in nodes:
        waylist = []
        cur_node = node
        waylist.append(cur_node)
        while True:
            pid = cur_node[6]
            idx = idlist.index(pid)
            next_node = swc[idx]
            waylist.append(next_node)
            if next_node == soma:
                break
            cur_node = next_node
        waylists.append(waylist)
    return waylists


def stem_reconstruct(swc, waylists, R):
    '''

    :param swc: swc list
    :param waylists: the way of nodes to soma
    :param R: radius of soma
    :return: new swc list
    '''
    delete_id = []
    connect_id = []
    node_DistoSoma = {}  # node到soma的欧氏距离 id:distance
    soma = get_soma(swc)
    for node in swc:
        node_DistoSoma[node[0]] = Euc_calc(node[2], node[3], node[4], soma[2], soma[3], soma[4])


# Branch Mode!!!
def find_tips_to_soma(swc, issoma=True, temp_soma=None, restriction=[]):
    if issoma:
        soma = get_soma(swc)
        if not soma:
            return [], []
    else:
        soma = temp_soma
    tips = get_tips(swc)
    birfucations = get_bifurs(swc)
    if not tips or not birfucations:
        return [], []
    birfu_id = np.array(birfucations)[:, 0].tolist()
    soma_id = soma[0]
    total = []
    total_id = []
    for tip in tips:
        tmpQueue = []
        tmpId = []
        curnode = tip
        curpid = tip[6]
        curid = tip[0]
        tmpQueue.append(curnode)
        tmpId.append(int(curid))
        while True:
            try:
                nextidx = np.array(swc)[:, 0].tolist().index(curpid)
            except:
                tmpId = []
                tmpQueue = []
                break
            curnode = swc[nextidx]
            curpid = curnode[6]
            curid = curnode[0]

            if curid in birfu_id:
                tmpId.append(curid)
                tmpQueue.append(curnode)
            if curid == soma_id:
                tmpId.append(curid)
                tmpQueue.append(curnode)
                break
            if restriction:
                if curid in np.array(restriction)[:, 0]:
                    break
        if tmpId:
            tmpQueue.reverse()
            tmpId.reverse()
            total.append(tmpQueue)
            total_id.append(tmpId)

    return total_id, total


def calc_length(total_id, swc):
    dic = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {}, 9: {}, 10: {}}
    for pathway in total_id:
        for funci in range(len(pathway) - 1):
            if funci >= 10:
                break
            if pathway[funci] not in dic[funci + 1].keys():
                dic[funci + 1][pathway[funci]] = [pathway[funci + 1]]
            else:
                if pathway[funci + 1] not in dic[funci + 1][pathway[funci]]:
                    dic[funci + 1][pathway[funci]].append(pathway[funci + 1])
    return dic
    ids, pids = np.array(swc)[:, 0].tolist(), np.array(swc)[:, 6].tolist()
    dicc = {}
    for funci in range(1, 11, 1):  # {1: {1: [2, 51, 88, 111, 119, 128, 142]},
        onebranchdistance = []
        for key in dic[funci].keys():  # {1: [2, 51, 88, 111, 119, 128, 142]},
            for elem_id in dic[funci][key]:  # [2, 51, 88, 111, 119, 128, 142]
                distance = 0
                idx = ids.index(elem_id)
                x1, y1, z1 = swc[idx][2:5]
                pid = swc[idx][6]
                while True:
                    idx = ids.index(pid)
                    x2, y2, z2 = swc[idx][2:5]
                    distance += Euc_calc(x1, y1, z1, x2, y2, z2)
                    if swc[idx][0] == key:
                        break
                    x1, y1, z1 = x2, y2, z2
                    pid = swc[idx][6]
                onebranchdistance.append(distance)
        dicc[funci] = onebranchdistance

    return dicc


def find_pri_branch(swc_matrix):
    soma_list = []
    count = 0

    soma_list.append(get_soma(swc_matrix)[0])

    pri_node = []
    for funci in range(len(swc_matrix)):
        if swc_matrix[funci][6] in soma_list and swc_matrix[funci][1] != 1 and swc_matrix[funci][1] != 2:
            pri_node.append(swc_matrix[funci])
            count += 1
    return count, pri_node


def find_next_branch(swc_matrix, pri_id, bifurid):
    if len(pri_id) == 0:
        return []
    branch_list = []  # 放进去pri 出二级分支点， 放二级分支点 出3级
    for funci in range(len(pri_id)):
        cur_node = pri_id[funci]
        while True:
            for funcj in range(len(swc_matrix)):
                if swc_matrix[funcj][6] == cur_node:
                    cur_node = swc_matrix[funcj][0]
                    break
            if cur_node in bifurid:
                branch_list.append(cur_node)
                break
            elif cur_node not in bifurid and funcj == len(swc_matrix) - 1:
                break

    return branch_list


def swc_radius_trim(swc, R):
    swclist = []
    idlist = np.array(swc)[:, 0]
    pidlist = np.array(swc)[:, 6]
    bifur_child = {}
    bifur_marker = {}
    soma = get_soma(swc)
    if not soma:
        return []
    curpathbifuridlist = []  # 当前路径的soma、bifur

    curnodeid = soma[0]

    while True:
        curnode = swc[np.argwhere(idlist == curnodeid).flatten()[0]]
        if Euc_calc(soma[2], soma[3], soma[4], curnode[2], curnode[3], curnode[4]) > R:
            curnodeid = curpathbifuridlist[-1]
            continue

        curnodechildid = np.sort(idlist[np.argwhere(pidlist == curnodeid).flatten()])  # 小到大排序

        if len(curnodechildid) > 1 or curnodeid == soma[0]:
            if curnodeid not in bifur_child.keys():
                bifur_child[curnodeid] = curnodechildid
                bifur_marker[curnodeid] = np.array([False] * len(curnodechildid))
                swclist.append(swc[np.argwhere(idlist == curnodeid).flatten()[0]])
                curpathbifuridlist.append(curnodeid)
            curidx = np.argwhere(bifur_marker[curnodeid] == False).flatten()
            notsearchedchildid = bifur_child[curnodeid][curidx]
            if len(notsearchedchildid) == 0:
                # 为空则返回上一个bifur/soma
                curpathbifuridlist.remove(curnodeid)
                if curpathbifuridlist:
                    curnodeid = curpathbifuridlist[-1]
                else:
                    return swclist
            else:  # 不为空
                tmp = bifur_marker[curnodeid]
                tmp[curidx[0]] = True  # 被搜到了
                bifur_marker.update({curnodeid: tmp})
                curnodeid = bifur_child[curnodeid][curidx][0]
        elif len(curnodechildid) == 0:  # 叶节点
            swclist.append(swc[np.argwhere(idlist == curnodeid).flatten()[0]])
            curnodeid = curpathbifuridlist[-1]
        else:
            swclist.append(swc[np.argwhere(idlist == curnodeid).flatten()[0]])
            curnodeid = curnodechildid[0]


def Vaa3d_global_feature(swcpath):
    try:
        col_name = []
        vaa3d_path = "D:/Vaa3D_V3.601_Windows_MSVC_64bit/"
        a = os.popen("{}vaa3d_msvc.exe /x {}"
                     "plugins/neuron_utilities/global_neuron_feature/global_neuron_feature.dll "
                     "/f compute_feature "
                     "/i \"{}\"".format(vaa3d_path, vaa3d_path, swcpath.replace("\\", "/")))
        emm = a.readlines()
        count = 0
        temp = []
        value = []
        for i in range(len(emm)):
            if count == 1:
                temp.append(emm[i])
            if emm[i] == "compute Feature  \n":
                count = 1
        temp.pop(-1)
        for i in range(len(temp)):
            spli = temp[i].split(":")
            cn = spli[0]
            if cn == "Number of Bifurcatons":
                cn = "Number of Bifurcations"
            col_name.append(cn)
            aa = re.search("\d+.\d+e\+\d+", spli[1])
            bb = re.search("\d+e\+\d+", spli[1])
            cc = re.search("\d+\.\d+", spli[1])
            dd = re.search("\d+", spli[1])
            if aa is not None and bb is not None and cc is not None and dd is not None:
                value.append(float(aa.group()))
            elif aa is None and bb is not None and cc is None:
                value.append(float(bb.group()))
            elif aa is None and bb is None and cc is not None:
                value.append(float(cc.group()))
            else:
                value.append(float(dd.group()))
        if len(value) <= 22:
            return [None] * 28, col_name
        else:
            return value, col_name
    except:
        return [None] * 28, [None] * 28


def get_path(path):
    path_list = []
    iter_f = os.walk(path)
    root_path = ""
    file_path_list = ""
    try:
        while True:
            cur = next(iter_f)
            root_path = cur[0]
            file_path_list = cur[-1]
            if not file_path_list:
                continue
            for i in range(len(file_path_list)):
                path = os.path.join(root_path, file_path_list[i])
                path_list.append(path)

    except StopIteration:
        pass

    return path_list


def detail_to_rough_region(df, target=None, color=False):
    with open(r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Scripts\neuron_code\neuron\tree.json") as f:
        tree = json.load(f)

    if target is None:
        with open(r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Tables\acronym_list_1.txt") as f:
            rough_region = [x.strip("\n") for x in f.readlines()]

        # rough_region.remove("Isocortex")
        rough_region.remove("fiber tracts")
        # rough_region = ["MO"]+rough_region
    else:
        rough_region = target

    colordict = {}

    # 获取rough脑区的id
    rr_id = {}
    for item in tree:
        if item["acronym"] in rough_region:
            rr_id[item["id"]] = item["acronym"]
            colordict[item["acronym"]] = np.array(item["rgb_triplet"]) / 255.0

    mapdict = {}
    for ct in df["CellType"].value_counts().index:
        for item in tree:
            if item["acronym"] == ct:
                cur_path = item["structure_id_path"]
                for rrid in rr_id.keys():
                    if rrid in cur_path:
                        mapdict[ct] = rr_id[rrid]
                        break
                    else:
                        mapdict[ct] = "unknown"
    if not color:
        return mapdict
    else:
        return mapdict, colordict


def recon_mesh(img, fname_output, fname_tmp='./tmp.mhd', color=None):
    mask = img.copy()
    mask[img > 0] = 255
    snew = sitk.GetImageFromArray(mask)
    sitk.WriteImage(snew, fname_tmp)

    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(fname_tmp)
    reader.Update()

    iso = vtk.vtkMarchingCubes()
    iso.SetInputConnection(reader.GetOutputPort())
    iso.SetValue(0, 1)
    iso.ComputeNormalsOff()
    iso.Update()
    mesh = iso.GetOutput()

    smoother = vtk.vtkSmoothPolyDataFilter()
    smoother.SetInputData(mesh)
    smoother.SetNumberOfIterations(500)
    smoother.SetRelaxationFactor(0.1)
    smoother.FeatureEdgeSmoothingOff()
    smoother.BoundarySmoothingOn()
    smoother.Update()
    mesh = smoother.GetOutput()

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(mesh)
    normals.SetFeatureAngle(100.0)
    normals.ComputePointNormalsOn()
    normals.SplittingOn()
    normals.Update()
    mesh = normals.GetOutput()

    if color is not None:
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        for _ in range(mesh.GetNumberOfPoints()):
            colors.InsertNextTypedTuple(color)
        mesh.GetPointData().SetScalars(colors)

    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(fname_output)
    writer.SetInputData(mesh)
    writer.Update()


def calc_projection(swc, anno, scale=1 / 25):
    def calc_2nodes_dist(node1, node2):
        dist = np.linalg.norm(np.array(node1)[2:5] - np.array(node2)[2:5])
        return dist

    # mat = MouseAnatomyTree()
    # proj_dict = {0: 0.0}
    # for i in list(mat.lutidtoname.keys()):
    #     proj_dict[i] = 0.0
    proj_dict = {0: 0.0}
    for i in np.unique(anno):
        proj_dict[i] = 0.0

    NeuronHash = {}
    indexChildren = []
    for i in range(len(swc)):
        NeuronHash[swc[i][0]] = i
        indexChildren.append([])
    for i in range(len(swc)):
        pid = swc[i][6]
        idx = NeuronHash.get(pid)
        if idx is None: continue
        indexChildren[idx].append(i)

    # DBS
    root = get_soma(swc)
    if len(root) == 0: return proj_dict
    root_n = root[0]
    root_idx = NeuronHash[root_n]

    bifurs_chs = indexChildren[root_idx]
    cur_idx = root_idx
    cur_node = root
    while bifurs_chs:
        next_idx = bifurs_chs.pop()
        next_node = swc[next_idx]
        cur_idx = NeuronHash[next_node[6]]
        cur_node = swc[cur_idx]
        tmpdist = calc_2nodes_dist(cur_node, next_node)
        # print(f'tmpdist:{tmpdist}',cur_idx,next_idx,'outer')
        mid_pos_25um = np.round((np.array(cur_node)[2:5] + np.array(next_node)[2:5]) / 2.0 * scale).astype(int)

        if ((mid_pos_25um[0] >= 0) & (mid_pos_25um[0] < anno.shape[0]) &
                (mid_pos_25um[1] >= 0) & (mid_pos_25um[1] < anno.shape[1]) &
                (mid_pos_25um[2] >= 0) & (mid_pos_25um[2] < anno.shape[2])):
            key = anno[mid_pos_25um[0], mid_pos_25um[1], mid_pos_25um[2]]
            proj_dict[key] += tmpdist
        else:
            proj_dict[0] += tmpdist

        cur_idx = next_idx
        cur_node = next_node
        cur_child_idx_list = indexChildren[cur_idx]

        while len(cur_child_idx_list) == 1:
            next_idx = cur_child_idx_list[0]
            next_node = swc[next_idx]
            tmpdist = calc_2nodes_dist(cur_node, next_node)
            # print(f'tmpdist:{tmpdist}',cur_idx,next_idx,'inner')
            mid_pos_25um = np.round((np.array(cur_node)[2:5] + np.array(next_node)[2:5]) / 2.0 * scale).astype(int)

            if ((mid_pos_25um[0] >= 0) & (mid_pos_25um[0] < anno.shape[0]) &
                    (mid_pos_25um[1] >= 0) & (mid_pos_25um[1] < anno.shape[1]) &
                    (mid_pos_25um[2] >= 0) & (mid_pos_25um[2] < anno.shape[2])):
                key = anno[mid_pos_25um[0], mid_pos_25um[1], mid_pos_25um[2]]
                proj_dict[key] += tmpdist
            else:
                proj_dict[0] += tmpdist

            cur_idx = next_idx
            cur_node = next_node
            cur_child_idx_list = indexChildren[cur_idx]

        if len(cur_child_idx_list) > 1:
            bifurs_chs.extend(cur_child_idx_list)
        elif len(cur_child_idx_list) == 0:
            continue

    return proj_dict


def calc_voxel_occupying(swc, anno, scale=1 / 25):
    # def calc_2nodes_dist(node1, node2):
    #     dist = np.linalg.norm(np.array(node1)[2:5] - np.array(node2)[2:5])
    #     return dist
    def calc_2nodes_interp(node1, node2):
        nodelist = [np.array(node1)[2:5]]
        weightlist = [1]
        dist = np.linalg.norm(np.array(node1)[2:5] - np.array(node2)[2:5])
        normv = (np.array(node2)[2:5] - np.array(node1)[2:5]) / dist
        if dist // 1 >= 1:
            for tmpi in range(int(dist // 1)):
                nodelist.append(np.array(node1)[2:5] + (tmpi + 1) * normv)
        nodelist.append(np.array(node2)[2:5])
        return nodelist

    allvoxels = []
    voxelfill = np.zeros(anno.shape, dtype=np.uint8)

    NeuronHash = {}
    indexChildren = []
    for i in range(len(swc)):
        NeuronHash[swc[i][0]] = i
        indexChildren.append([])
    for i in range(len(swc)):
        pid = swc[i][6]
        idx = NeuronHash.get(pid)
        if idx is None: continue
        indexChildren[idx].append(i)

    # DBS
    root = get_soma(swc)
    if len(root) == 0: return voxelfill
    root_n = root[0]
    root_idx = NeuronHash[root_n]

    bifurs_chs = indexChildren[root_idx]
    cur_idx = root_idx
    cur_node = root
    while bifurs_chs:
        next_idx = bifurs_chs.pop()
        next_node = swc[next_idx]
        cur_idx = NeuronHash[next_node[6]]
        cur_node = swc[cur_idx]
        nodelist = calc_2nodes_interp(cur_node, next_node)
        allvoxels.extend(nodelist)

        cur_idx = next_idx
        cur_node = next_node
        cur_child_idx_list = indexChildren[cur_idx]

        while len(cur_child_idx_list) == 1:
            next_idx = cur_child_idx_list[0]
            next_node = swc[next_idx]
            nodelist = calc_2nodes_interp(cur_node, next_node)
            allvoxels.extend(nodelist)

            cur_idx = next_idx
            cur_node = next_node
            cur_child_idx_list = indexChildren[cur_idx]

        if len(cur_child_idx_list) > 1:
            bifurs_chs.extend(cur_child_idx_list)
        elif len(cur_child_idx_list) == 0:
            continue

    allvoxels = np.asarray(allvoxels)
    if allvoxels.size == 0: return voxelfill
    allvoxels = np.round(allvoxels).astype(int)
    allvoxels = allvoxels[(allvoxels[:, 0] >= 0) & (allvoxels[:, 0] < anno.shape[0]) &
                          (allvoxels[:, 1] >= 0) & (allvoxels[:, 1] < anno.shape[1]) &
                          (allvoxels[:, 2] >= 0) & (allvoxels[:, 2] < anno.shape[2])]
    voxelfill[allvoxels[:, 0], allvoxels[:, 1], allvoxels[:, 2]] = 1

    return voxelfill


def genObj(input_p, ntype=None, scale=1.0, output_p='./tmp/tmp.obj'):
    swcraw = read_swc(input_p, scale=scale)
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
        line = 'v ' + str(swc[i][2]) + ' ' + str(swc[i][3]) + ' ' + str(swc[i][4]) + '\n'
        objLines.append(line)
    for i in range(0, len(swc)):
        p = swc[i][6]
        if p not in NeuronHash.keys():
            continue
        line = 'l ' + str(i + 1) + ' ' + str(NeuronHash[p] + 1) + '\n'
        objLines.append(line)

    with open(output_p, 'w') as f:
        f.writelines(objLines)


class SWC_Features:
    '''
    some new features. (see feature_name)
    (swc need resample)
    '''

    def __init__(self, swc, swcname, swc_reg=None):
        self.feature_name = ["Average Euclidean Distance", "25% Euclidean Distance", "50% Euclidean Distance",
                             "75% Euclidean Distance", "Average Path Distance", "25% Path Distance",
                             "50% Path Distance", "75% Path Distance", "Center Shift", "Relative Center Shift"]

        self.features = []
        self.swc = swc
        self.swcname = swcname
        self.soma = get_soma(swc)
        self.tips = get_tips(swc)
        self.swc_reg = swc_reg
        # self.bifurs = get_bifurs(swc)

        if not self.soma:
            print(swcname, "no soma detected...")
            self.features = []
        else:
            self.features += self.Euc_Dis(swc)
            self.features += self.Pat_Dis(swc)
            cs = self.center_shift(swc)
            ave_euc_dis = self.features[0]
            self.features += [cs, cs / ave_euc_dis]
            if self.swc_reg is not None:
                self.features += self.size_related_features(swc_reg)
                self.features += self.xyz_approximate(swc_reg)
                self.feature_name += [
                    "Area", 'Volume', "2D Density", "3D Density", "Width", "Height", "Depth", "Width_95ci",
                    "Height_95ci",
                    "Depth_95ci", "Slimness", "Flatness", "Slimness_95ci", "Flatness_95ci"]

    def Euc_Dis(self, swc):
        dislist = []
        soma = self.soma
        for node in swc:
            cur_dis = Euc_calc(soma[2], soma[3], soma[4], node[2], node[3], node[4])
            dislist.append(cur_dis)
        length = len(dislist)
        if length == 0:
            return [None] * 4
        euc_dis_ave = np.mean(dislist)
        dislist.sort()
        euc_dis_25 = dislist[int(np.floor(length * 1 / 4))]
        euc_dis_50 = np.median(dislist)
        euc_dis_75 = dislist[int(np.floor(length * 3 / 4))]
        return [euc_dis_ave, euc_dis_25, euc_dis_50, euc_dis_75]

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
                    cur_dist = Euc_calc(self.soma[2], self.soma[3], self.soma[4], node[2], node[3], node[4])
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
                delta_pathdist = Euc_calc(cur_node[2], cur_node[3], cur_node[4], new_node[2], new_node[3], new_node[4])
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
            return [None] * 4
        path_dis_ave = np.mean(pathdislist)
        pathdislist.sort()
        path_dis_25 = pathdislist[int(np.floor(length * 1 / 4))]
        path_dis_50 = np.median(pathdislist)
        path_dis_75 = pathdislist[int(np.floor(length * 3 / 4))]
        return [path_dis_ave, path_dis_25, path_dis_50, path_dis_75]

    def center_shift(self, swc):
        soma = self.soma
        swc_ar = np.array(swc)
        centroid = np.mean(swc_ar[:, 2:5], axis=0)
        return Euc_calc(soma[2], soma[3], soma[4], centroid[0], centroid[1], centroid[2])

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
        if num_nodes < 3:
            return [None] * 4
        swc_zy = np.array(swc)[:, 3:5]
        swc_xyz = np.array(swc)[:, 2:5]
        CH2D = ConvexHull(swc_zy)
        CH3D = ConvexHull(swc_xyz)
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
                count = int(Euc_calc(x1, y1, z1, x2, y2, z2) // 1)
                if count != 0:
                    tmp = [[x1 + 1 * x, y1 + 1 * x, z1 + 1 * x] for x in
                           range(1, count + 1)]
                    swc_xyz_new.extend(tmp)

        num_pixels, num_voxels = self.pixel_voxel_calc(swc_xyz_new)
        density_2d = num_pixels / area
        density_3d = num_voxels / volume

        return [area, volume, density_2d, density_3d]

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

        return [width, height, depth, width_95ci, height_95ci, depth_95ci, slimness, flatness, slimness_95ci,
                flatness_95ci]


class MouseAnatomyTree:
    def __init__(self, treepath=r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Tables\tree.json", ):
        self.tree = []
        self.roughlist = ['Isocortex', 'OLF', 'HPF', 'CTXsp', 'STR', 'PAL',
                          'TH', 'HY', 'MB', 'P', 'MY', 'CBX', 'CBN', 'VS', 'fiber tracts']
        self.lutnametoid = {}
        self.lutidtoname = {}
        self.lutidtorgb = {}
        self.lutnametorough = {}

        self._id_index_hash = {}

        with open(treepath) as f:
            self.tree = json.load(f)

        for i, t in enumerate(self.tree):
            id_ = t["id"]
            self.lutnametoid[t["acronym"]] = id_
            self.lutidtoname[id_] = t["acronym"]
            self.lutidtorgb[id_] = t["rgb_triplet"]
            self._id_index_hash[id_] = i

        for t in self.tree:
            self.lutnametorough[t['acronym']] = t['acronym']
            for rough in self.roughlist:
                if self.lutnametoid.get(rough) in t['structure_id_path']:
                    self.lutnametorough[t['acronym']] = rough
                    break

    def _id_acronym_check(self, inp, inp_type: str):
        if inp_type not in ['id', 'acronym']:
            raise ValueError(f'invalid input type: {inp_type}, should be one of "id", "acronym".')
        if inp_type == 'id':
            if isinstance(inp, str):
                inp = self.lutnametoid.get(inp)
        elif inp_type == 'acronym':
            if isinstance(inp, int):
                inp = self.lutidtoname.get(inp)
        return inp

    def _ctlist_overlap_check(self, ctlist) -> bool:
        # check ctlist whether it has overlapping cell types in tree hireachy
        ct_child_list = []
        for ct in ctlist:
            ct = self._id_acronym_check(ct, 'id')
            children = self.find_children_id(ct)

            if ct in ct_child_list:
                return True

            ct_child_list.extend(children)

        return False

    def find_children_id(self, id_):
        id_ = self._id_acronym_check(id_, 'id')
        idlist = []
        for t in self.tree:
            if id_ in t["structure_id_path"]:
                idlist.append(t['id'])
        if not idlist:
            idlist = [id_]
        return idlist

    def ccf_sort(self, ctlist):
        select_ct_sorted = []
        for item in self.tree:
            if item["acronym"] in ctlist:
                select_ct_sorted.append(item["acronym"])
        return select_ct_sorted

    def cortex_layer_to_upper(self, ctlist, SSp=False):
        newctlist = []
        _SSp_id = self.lutnametoid['SSp']
        for ct in ctlist:
            ct = self._id_acronym_check(ct, 'acronym')
            if self.lutnametorough.get(ct) == 'Isocortex':
                id_ = self.lutnametoid.get(ct)
                upper_id_list = self.tree[self._id_index_hash[id_]]['structure_id_path']
                if len(upper_id_list) >= 2:
                    upper_id = upper_id_list[-2]
                else:
                    upper_id = upper_id_list[-1]
                upper_acronym = self.lutidtoname.get(upper_id)

                if SSp:
                    if _SSp_id in upper_id_list:
                        upper_acronym = 'SSp'
                        newctlist.append(upper_acronym)
                        continue

                if ct[len(upper_acronym):] in ['1', '2/3', '4', '5', '6', '6a', '6b']:
                    newctlist.append(upper_acronym)
                else:
                    newctlist.append(ct)
            else:
                newctlist.append(ct)

        return newctlist

    def ctlist_to_given_ctlist(self, ctlist, given_ctlist, not_in_set_None=False):
        # bullshit code need to re-write
        overlap_flag = self._ctlist_overlap_check(given_ctlist)
        if overlap_flag:
            raise ValueError('given_ctlist has overlapping cell types')
        ctlist = np.asarray(ctlist)
        given_ctlist = np.asarray(given_ctlist)
        tmp_ctlist = []
        tmp_given_ctlist = []
        for ct in ctlist:
            ct = self._id_acronym_check(ct, 'id')
            tmp_ctlist.append(ct)
        tmp_ctlist = np.asarray(tmp_ctlist)

        out_arr = np.zeros(len(tmp_ctlist), dtype=object)
        if not_in_set_None:
            out_arr[out_arr == 0] = None
        else:
            out_arr = np.asarray(tmp_ctlist, dtype=object)

        for gct in given_ctlist:
            gct_children = self.find_children_id(gct)
            out_arr[np.isin(tmp_ctlist, gct_children)] = gct

        for i in range(len(out_arr)):
            out_arr[i] = self._id_acronym_check(out_arr[i], 'acronym')

        return out_arr


if __name__ == "__main__":
    print()
    MAT = MouseAnatomyTree()
    print(MAT.cortex_layer_to_upper(['SSp-bfd2/3'], SSp=True))
    print(MAT.lutnametorough['POR'])

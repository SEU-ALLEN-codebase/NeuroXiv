# xuan
import os
from typing import Dict, List
import time
import math

import matplotlib.pyplot as plt


def DISTP(p1, p2):
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2 + (p1.z - p2.z) ** 2) ** 0.5


def angle(a, b, c):
    return (math.acos(((b.x - a.x) * (c.x - a.x) + (b.y - a.y) * (c.y - a.y) + (b.z - a.z) * (c.z - a.z)) / (
            DISTP(a, b) * DISTP(a, c) + 1e-7)) * 180.0 / math.pi)


class NeuronSwc():
    def __init__(self, n, x, y, z, type, r, parent) -> None:
        self.n = n
        self.x = x
        self.y = y
        self.z = z
        self.type = type
        self.r = r
        self.parent = parent


class Point():
    def __init__(self, n, x, y, z, type, r, pn=None) -> None:
        self.n = n
        self.x = x
        self.y = y
        self.z = z
        self.type = type
        self.r = r
        self.pn = pn
        self.childNum = 0


class NeuronTree():
    '''

    '''

    def __init__(self) -> None:
        self.NeuronList = []
        self.NeuronHash = {}
        self.indexChildren = []
        self.path = ""
        self.resetFeature()

    def initial(self):
        self.NeuronHash = {}
        self.indexChildren = []
        for i in range(0, len(self.NeuronList)):
            self.NeuronHash[self.NeuronList[i].n] = i
            self.indexChildren.append([])
        for i in range(0, len(self.NeuronList)):
            p = self.NeuronList[i].parent
            if p not in self.NeuronHash.keys():
                if self.rootidx == -1:
                    self.rootidx = i
                continue
            self.indexChildren[self.NeuronHash[p]].append(i)

    def resetFeature(self):
        self.Width = 0
        self.Height = 0
        self.Depth = 0
        self.Diameter = 0
        self.Length = 0
        self.Volume = 0
        self.Surface = 0
        self.Hausdorff = 0
        self.N_node = 0
        self.N_stem = 0
        self.N_bifs = 0
        self.N_branch = 0
        self.N_tips = 0
        self.Max_Order = 0
        self.Pd_ratio = 0
        self.Contraction = 0
        self.Max_Eux = 0
        self.Max_Path = 0
        self.BifA_local = 0
        self.BifA_remote = 0
        self.Soma_surface = 0
        self.Fragmentation = 0
        self.rootidx = -1
        self.pathTotal = []
        self.euxTotal = []

    def readSwc(self, path):
        self.path = path
        with open(self.path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if '#' in line:
                    continue
                ss = line.split(' ')
                s = NeuronSwc(int(ss[0]),
                              float(ss[2]), float(ss[3]), float(ss[4]),
                              int(ss[1]), float(ss[5]), int(ss[6]))
                self.NeuronList.append(s)
        self.initial()

    def readSwc_fromlist(self, swclist):
        self.NeuronList = []
        for ss in swclist:
            s = NeuronSwc(int(ss[0]),
                          float(ss[2]), float(ss[3]), float(ss[4]),
                          int(ss[1]), float(ss[5]), int(ss[6]))
            self.NeuronList.append(s)
        self.initial()

    def writeSwc(self, path):
        swcLines = []
        for s in self.NeuronList:
            line = "{} {} {:.3f} {:.3f} {:.3f} {} {}\n".format(s.n, s.type, s.x, s.y, s.z, s.r, s.parent)
            swcLines.append(line)
        with open(path, 'w') as f:
            f.writelines(swcLines)

    def resamplePath(self, seg: List[Point], step: float):
        segR = []
        pathLength = 0
        start = seg[0]
        segPar = seg[-1].pn
        iterOld = 0
        segR.append(start)
        size = len(seg)

        while iterOld < size and start and start.pn:
            pathLength += DISTP(start, start.pn)
            if pathLength <= len(segR) * step:
                start = start.pn
                iterOld += 1
            else:
                pathLength -= DISTP(start, start.pn)
                rate = (len(segR) * step - pathLength) / DISTP(start, start.pn)
                pt = Point(start.n,
                           start.x + rate * (start.pn.x - start.x),
                           start.y + rate * (start.pn.y - start.y),
                           start.z + rate * (start.pn.z - start.z),
                           start.type,
                           start.r * (1 - rate) + start.pn.r * rate,
                           start.pn)

                segR[-1].pn = pt
                segR.append(pt)
                pathLength += DISTP(start, pt)
                start = pt
        segR[-1].pn = segPar
        return segR

    def resample(self, step):
        self.initial()
        result = NeuronTree()
        size = len(self.NeuronList)
        tree = []
        for i in range(0, size):
            s = self.NeuronList[i]
            pt = Point(s.n, s.x, s.y, s.z, s.type, s.r)
            pt.childNum = len(self.indexChildren[i])
            tree.append(pt)
        for i in range(0, size):
            if self.NeuronList[i].parent not in self.NeuronHash.keys():
                continue
            pIndex = self.NeuronHash[self.NeuronList[i].parent]
            tree[i].pn = tree[pIndex]
        segList = []
        for i in range(0, size):
            if tree[i].childNum != 1:
                seg = []
                cur = tree[i]
                seg.append(cur)
                cur = cur.pn
                while cur and cur.childNum == 1:
                    seg.append(cur)
                    cur = cur.pn
                segList.append(seg)

        for i in range(0, len(segList)):
            segList[i] = self.resamplePath(segList[i], step)

        indexMap = {}
        tree = []
        for i in range(0, len(segList)):
            for j in range(0, len(segList[i])):
                tree.append(segList[i][j])
                indexMap[tree[-1]] = len(tree) - 1
        rootidx = -1
        for i in range(0, len(tree)):
            p = tree[i]
            if p.pn is None:
                if rootidx==-1:
                    parent = -1
                    rootidx = i + 1
                else:
                    parent = rootidx
            else:
                parent = indexMap[p.pn] + 1
            s = NeuronSwc(i + 1, p.x, p.y, p.z, p.type, p.r, parent)
            result.NeuronList.append(s)

        result.initial()

        return result

    def computeFeature(self):
        self.initial()
        self.N_node = len(self.NeuronList)
        self.N_stem = len(self.indexChildren[self.rootidx])
        self.Soma_surface = 4 * math.pi * ((self.NeuronList[self.rootidx].r) ** 2)
        self.computeLinear()
        self.computeTree()

    def computeLinear(self):
        xmin = ymin = zmin = 100000
        xmax = ymax = zmax = -100000
        NeuronList = self.NeuronList
        soma = NeuronList[self.rootidx]
        for i in range(0, len(NeuronList)):
            curr = NeuronList[i]
            xmin = min(xmin, curr.x)
            ymin = min(ymin, curr.y)
            zmin = min(zmin, curr.z)
            xmax = max(xmax, curr.x)
            ymax = max(ymax, curr.y)
            zmax = max(zmax, curr.z)
            if len(self.indexChildren[i]) == 0:
                self.N_tips += 1
            elif len(self.indexChildren[i]) > 1:
                self.N_bifs += 1
            if curr.parent < 0:
                continue
            pIndex = self.NeuronHash[curr.parent]
            l = DISTP(curr, NeuronList[pIndex])
            self.Diameter += 2 * curr.r
            self.Length += l
            self.Surface += 2 * math.pi * curr.r * l
            self.Volume += math.pi * curr.r * l
            lsoma = DISTP(curr, soma)
            self.euxTotal.append(lsoma)
            self.Max_Eux = max(self.Max_Eux, lsoma)
        self.Width = xmax - xmin
        self.Height = ymax - ymin
        self.Depth = zmax - zmin
        self.Diameter /= len(NeuronList)

    def getRemoteChild(self, t):
        rchildlist = []
        for i in range(0, len(self.indexChildren[t])):
            tmp = self.indexChildren[t][i]
            while len(self.indexChildren[tmp]) == 1:
                tmp = self.indexChildren[tmp][0]
            rchildlist.append(tmp)
        return rchildlist

    def computeTree(self):
        NeuronList = self.NeuronList
        soma = NeuronList[self.rootidx]
        self.pathTotal = [0] * len(NeuronList)
        depth = [0] * len(NeuronList)
        stack = []
        stack.append(self.rootidx)
        pathlength = eudist = max_local_ang = max_remote_ang = 0
        N_ratio = N_Contraction = 0

        if len(self.indexChildren[self.rootidx]) > 1:
            max_local_ang = max_remote_ang = 0
            ch_local1 = self.indexChildren[self.rootidx][0]
            ch_local2 = self.indexChildren[self.rootidx][1]
            local_ang = angle(soma, NeuronList[ch_local1], NeuronList[ch_local2])

            rchildlist = self.getRemoteChild(self.rootidx)
            ch_remote1 = rchildlist[0]
            ch_remote2 = rchildlist[1]
            remote_ang = angle(soma, NeuronList[ch_remote1], NeuronList[ch_remote2])

            max_local_ang = max(max_local_ang, local_ang)
            max_remote_ang = max(max_remote_ang, remote_ang)
            self.BifA_local += max_local_ang
            self.BifA_remote += max_remote_ang

        while len(stack):
            t = stack.pop()
            child = self.indexChildren[t]
            for i in range(0, len(child)):
                self.N_branch += 1
                tmp = child[i]
                if NeuronList[t].r > 0:
                    N_ratio += 1
                    self.Pd_ratio += NeuronList[tmp].r / NeuronList[t].r
                pathlength = DISTP(NeuronList[tmp], NeuronList[t])
                self.pathTotal[tmp] = self.pathTotal[t] + pathlength

                fragment = 0
                while len(self.indexChildren[tmp]) == 1:
                    ch = self.indexChildren[tmp][0]
                    pathlength += DISTP(NeuronList[ch], NeuronList[tmp])
                    self.pathTotal[ch] = self.pathTotal[tmp] + DISTP(NeuronList[ch], NeuronList[tmp])
                    fragment += 1
                    tmp = ch
                eudist = DISTP(NeuronList[tmp], NeuronList[t])
                self.Fragmentation += fragment
                if pathlength > 0:
                    self.Contraction += eudist / pathlength
                    N_Contraction += 1

                chsz = len(self.indexChildren[tmp])
                if chsz > 1:
                    stack.append(tmp)

                    max_local_ang = max_remote_ang = 0
                    ch_local1 = self.indexChildren[tmp][0]
                    ch_local2 = self.indexChildren[tmp][1]
                    local_ang = angle(NeuronList[tmp], NeuronList[ch_local1], NeuronList[ch_local2])

                    rchildlist = self.getRemoteChild(tmp)
                    ch_remote1 = rchildlist[0]
                    ch_remote2 = rchildlist[1]
                    remote_ang = angle(NeuronList[tmp], NeuronList[ch_remote1], NeuronList[ch_remote2])

                    self.BifA_local += local_ang
                    self.BifA_remote += remote_ang
                self.pathTotal[tmp] = self.pathTotal[t] + pathlength
                depth[tmp] = depth[t] + 1

        self.Pd_ratio /= N_ratio + 1e-7
        self.Fragmentation /= self.N_branch + 1e-7
        self.Contraction /= N_Contraction + 1e-7

        self.BifA_local /= self.N_bifs + 1e-7
        self.BifA_remote /= self.N_bifs + 1e-7

        for i in range(0, len(NeuronList)):
            self.Max_Path = max(self.Max_Path, self.pathTotal[i])
            self.Max_Order = max(self.Max_Order, depth[i])

    def splitDendriteAxon(self):
        dendrite = NeuronTree()
        axon = NeuronTree()
        for ns in self.NeuronList:
            # if ns.type in [2]:
            #     axon.NeuronList.append(ns)
            if True:
                dendrite.NeuronList.append(ns)
        axon.initial()
        dendrite.initial()
        return axon, dendrite

    def saveObj(self, path):
        objLines = []
        for i in range(0, len(self.NeuronList)):
            NeuronList = self.NeuronList
            line = 'v ' + str(NeuronList[i].x) + ' ' + str(NeuronList[i].y) + ' ' + str(NeuronList[i].z) + '\n'
            objLines.append(line)
        for i in range(0, len(self.NeuronList)):
            p = self.NeuronList[i].parent
            if p not in self.NeuronHash.keys():
                continue
            line = 'l ' + str(i + 1) + ' ' + str(self.NeuronHash[p] + 1) + '\n'
            objLines.append(line)
        with open(path, 'w') as f:
            f.writelines(objLines)


# hanbo
import numpy as np
import math
from scipy import linalg as LA
from scipy.spatial.transform import Rotation as R


class Vertex():
    def __init__(self,
                 vid,
                 coordinate,
                 ntype,
                 parent=-1,
                 radius=1.):
        self.vid = vid
        self.coord = coordinate
        self.type = ntype
        self.radius = radius
        self.parent = parent
        self.child = []
        self.labels = {}
        self.len = 0

    def add_child(self, child_id):
        self.child.append(child_id)

    def add_label(self, name, value):
        if isinstance(value, (int, float)):
            self.labels[name] = [value]
        elif isinstance(value, (tuple, list)):
            self.labels[name] = value
        else:
            print("error: cannot recognize type of vertex lable %s:" % name, value)
            exit(0)


class PCA():
    def __init__(self):
        self.evecs = None

    def fit(self, x):
        cov = np.cov(x, rowvar=False)
        evals, evecs = LA.eigh(cov)
        idx = np.argsort(evals)[::-1]
        evecs = evecs[:, idx]
        evals = evals[idx]
        self.evecs = evecs

    def transform(self, x):
        if self.evecs is not None:
            return np.dot(x, self.evecs)
        else:
            return x


class Neuron():
    def __init__(self):
        self.reset()

    def reset(self):
        self.vertices = []
        self.dict_vid_to_index = {}
        self.roots = []
        self.labels = {}
        self.fname = ''
        self.roots_dir = []
        self.ntype = []

    def warning(self, msg):
        print('WARNING: file %s, %s' % (self.fname, msg))

    def load_eswc(self, swclist):
        # clean existing file
        self.reset()

        # parse lines
        list_pvid_cvid_pair = []
        for items in swclist:
            try:
                vid = int(items[0])
                ntype = int(items[1])
                self.ntype.append(ntype)
                coord = np.array([float(x) for x in items[2:5]])
                radius = float(items[5])
                parent_vid = int(items[6])
            except:
                self.warning('skip row when parsing: %s' % items)
                continue

            if vid in self.dict_vid_to_index:
                self.warning('ignore duplicate vertices: %s' % items)
                continue

            self.dict_vid_to_index[vid] = len(self.vertices)
            self.vertices.append(Vertex(vid, coord, ntype, radius=radius))
            if parent_vid != vid:
                list_pvid_cvid_pair.append((parent_vid, vid))
            else:
                self.warning('ignore self connection node: %s' % items)

            for lid in range(len(items[7:])):
                label = items[lid + 7]
                if label[0] == '#':  # comment
                    self.vertices[-1].add_label('comment', ' '.join(items[(lid + 7):]))
                    break
                try:
                    self.vertices[-1].add_label('label_%d' % lid, float(label))
                except:
                    self.warning('cannot recognize column %d: %s, use default value -1.' % (lid + 7, items))
                    self.vertices[-1].add_label('label_%d' % lid, -1)

        # update parent to child
        for pvid, cvid in list_pvid_cvid_pair:
            if pvid not in self.dict_vid_to_index:
                cidx = self.dict_vid_to_index[cvid]
                self.roots.append(cidx)
                self.vertices[cidx].len = 0
                continue
            if cvid not in self.dict_vid_to_index:
                # this should not happen
                self.warning('missing vertex with id %d, check code.' % cvid)
                exit()
            pidx = self.dict_vid_to_index[pvid]
            cidx = self.dict_vid_to_index[cvid]
            self.vertices[pidx].add_child(cidx)
            self.vertices[cidx].parent = pidx
            self.vertices[cidx].len = np.linalg.norm(self.vertices[pidx].coord - self.vertices[cidx].coord)

        if len(self.vertices) == 0:
            self.warning('empty reconstruction')

    def normalize_neuron(self, flag_rotate=True, ntype=None, dir_order='xyz'):
        if len(self.vertices)==0:
            return
        if ntype is None:
            ntype = [3, 4]
        if len(self.roots) > 1:
            self.warning('has multiple roots, use the first 1 as center')
        center = np.array(self.vertices[self.roots[0]].coord)
        for vidx, vtx in enumerate(self.vertices):
            tmp_coord = self.vertices[vidx].coord
            tmp_coord -= center
            self.vertices[vidx].coord = np.array(tmp_coord)
        if flag_rotate:
            self.rotate_neuron_by_pca_meanshift(ntype=ntype, dir_order=dir_order)

    def _vector_decouple(self, vec_tar, vec_ref):
        vec_ref = np.array(vec_ref)
        vec_ref /= np.linalg.norm(vec_ref)
        vec_tar -= vec_ref * np.dot(vec_tar, vec_ref)
        vec_tar /= np.linalg.norm(vec_tar)
        return vec_tar

    def _vector_to_vectors_cos(self, a_norm, b):
        return np.dot(a_norm.T, b.T) / (np.linalg.norm(b, axis=1) + 1e-16)

    def _vector_cos(self, a_norm, b):
        return np.dot(a_norm, b) / (np.linalg.norm(b) + 1e-16)

    def _angle_range_sample_searcher(self, init_dir, search_angle, ntype=None, constrain_dir=None):
        thr_angle = math.cos(math.pi / 180.0 * search_angle)
        init_dir = np.array(init_dir)
        init_dir /= np.linalg.norm(init_dir)
        sample_dir = np.array([vtx.coord for vtx in self.vertices if ntype is None or vtx.type in ntype])
        sample_weight = np.array(
            [vtx.len * np.linalg.norm(vtx.coord) for vtx in self.vertices if ntype is None or vtx.type in ntype])
        if constrain_dir is not None:
            constrain_dir = np.array(constrain_dir)
            constrain_dir /= np.linalg.norm(constrain_dir)
            project_dir = constrain_dir[:, np.newaxis] * np.dot(constrain_dir.T, sample_dir.T)
            sample_dir -= project_dir.T
        angle = self._vector_to_vectors_cos(init_dir, sample_dir)
        return np.sum(sample_weight[angle > thr_angle])

    def _mean_shift_direction_searcher(self, init_dir, search_angle, ntype=None, constrain_dir=None):
        thr_angle = math.cos(math.pi / 180.0 * search_angle)
        init_dir = np.array(init_dir)
        init_dir /= np.linalg.norm(init_dir)
        sample_dir = np.array([vtx.coord * vtx.len for vtx in self.vertices if ntype is None or vtx.type in ntype])
        if constrain_dir is not None:
            constrain_dir = np.array(constrain_dir)
            constrain_dir /= np.linalg.norm(constrain_dir)
            project_dir = constrain_dir[:, np.newaxis] * np.dot(constrain_dir.T, sample_dir.T)
            sample_dir -= project_dir.T
        angle = self._vector_to_vectors_cos(init_dir, sample_dir)
        if np.sum(angle > thr_angle) == 0:
            return init_dir
        new_dir = np.sum(sample_dir[angle > thr_angle, :], axis=0)
        new_dir /= np.linalg.norm(new_dir)
        return new_dir

    def _rotate_neuron_by_transform(self, transform_coord):
        for vidx, vtx in enumerate(self.vertices):
            self.vertices[vidx].coord = transform_coord(vtx.coord)
        for idx in range(len(self.roots_dir)):
            self.roots_dir[idx] = transform_coord(self.roots_dir[idx])

    def _mean_shift_direction(self, init_dir, constrain_dir=None, search_angle=30, converge_thr=1, max_iter=16,
                              ntype=None):
        thr_angle = math.cos(math.pi / 180.0 * converge_thr)
        prev_dir = np.array(init_dir)
        for i in range(max_iter):
            new_dir = self._mean_shift_direction_searcher(prev_dir, search_angle, ntype=ntype,
                                                          constrain_dir=constrain_dir)
            if self._vector_cos(prev_dir, new_dir) > thr_angle:
                break
            prev_dir = new_dir
        return new_dir

    def rotate_neuron_by_pca_meanshift(self, ntype=None, dir_order='zyx', attempt=0,
                                       search_angle_1=60):
        # use pca decide z direction
        pca = PCA()
        coord = np.array([vtx.coord for vtx in self.vertices if ntype is None or vtx.type in ntype])
        coord -= np.mean(coord, axis=0)
        if len(coord) < 3:
            return
        pca.fit(coord)
        dir_3 = pca.evecs[:, 2]
        coord = np.array([vtx.coord for vtx in self.vertices if ntype is None or vtx.type in ntype])
        tmp = np.dot(dir_3, coord.T)
        if np.sum(tmp) < 0:
            dir_3 *= -1

        # search primary direction with mean shift
        tmp_dir = [-1, 0, 0]
        if 1 - np.abs(np.dot(tmp_dir, dir_3)) < 1e-3:
            tmp_dir = [0, 1, 0]
        tmp_dir = self._vector_decouple(tmp_dir, dir_3)
        tmp_dir /= np.linalg.norm(tmp_dir)
        num_circle_samples = 6
        r = R.from_rotvec(np.pi / num_circle_samples * 2 * np.array(dir_3))
        max_weight = 0
        for i in range(num_circle_samples):
            tmp_weight = self._angle_range_sample_searcher(tmp_dir, search_angle_1, ntype, dir_3)
            if tmp_weight > max_weight:
                max_weight = tmp_weight
                dir_1 = tmp_dir
            tmp_dir = r.apply(tmp_dir)
        dir_1 = self._mean_shift_direction(dir_1, ntype=ntype, constrain_dir=dir_3,
                                           search_angle=search_angle_1)

        # use primary and last direction to decide secondary direction
        dir_2 = np.cross(dir_3, dir_1)
        coord = np.array([vtx.coord for vtx in self.vertices if ntype is None or vtx.type in ntype])
        tmp = np.dot(dir_2, coord.T)
        if np.sum(tmp) < 0:
            dir_2 *= -1

        def transform_coord(x):
            x = np.array(x)
            c1 = np.dot(x, dir_1)
            c2 = np.dot(x, dir_2)
            c3 = np.dot(x, dir_3)
            if dir_order == 'xyz':
                c_new = [c1, c2, c3]
            else:
                c_new = [c3, c2, c1]
            return np.array(c_new)

        self._rotate_neuron_by_transform(transform_coord)

        if attempt > 0:
            self.rotate_neuron_by_pca_meanshift(ntype, dir_order, attempt - 1)

    def convert_to_swclist(self):
        swclist = []
        for vtx in self.vertices:
            if vtx.parent >= 0:
                pid = self.vertices[vtx.parent].vid
            else:
                pid = -1

            swclist.append([vtx.vid, vtx.type, vtx.coord[0], vtx.coord[1], vtx.coord[2], vtx.radius, pid])

        return swclist


# ohters
def three_slice():
    '''
    create three-view slices of brain image
    '''

    import SimpleITK as sitk
    img = sitk.ReadImage(
        r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Tables\average_template_25.nrrd.UNIT8.v3draw.tiff")
    mask = np.array(np.load(r"E:\ZhixiYun\Projects\GitHub\neuro_morpho_toolbox\neuro_morpho_toolbox\data\ccf_25.pickle",
                            allow_pickle=True)[0]).astype(np.float32)
    mask[mask > 0] = 255
    mask = mask.astype(np.uint8)
    print(sitk.GetImageFromArray(mask[:, :, 0]))
    print(img.GetSize())
    img_arr = sitk.GetArrayFromImage(img).transpose([2, 1, 0])
    print(img_arr.shape)
    print(img_arr.dtype)
    print(np.max(img_arr),np.min(img_arr))
    for i in range(img_arr.shape[1]):
        sitk.WriteImage(sitk.GetImageFromArray((img_arr[:, img_arr.shape[1]-1-i,:])),
                        r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Model\slices\brain\axial_{}.png".format(i))
        sitk.WriteImage(sitk.GetImageFromArray(mask[:, i,:]),
                        r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Model\slices\mask\axial_{}_mask.png".format(
                            i))

    # plt.figure()
    # plt.imshow(img_arr[200], cmap='gray')
    # plt.show()


if __name__ == '__main__':
    print()

    # path = r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Dataset\Axon_All\1741_All\17109_1801_x6698_y12550.auto_r.swc"
    # path = r"D:\zx\tencent\网站\test_data\17109_1701_x8048_y22277.semi_r(1).swc"
    # nt = NeuronTree()
    # nt.readSwc(path)
    # nt_resample = nt.resample(25)
    # nt_resample.writeSwc(r"D:\zx\tencent\网站\test_data\17109_1701_x8048_y22277.semi_r(1)_resample.swc")

    # folders = os.listdir(r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Web_Data")
    # folders_n = ["_".join(x.split("_")[1:-1]) for x in folders]
    # path = r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Dataset\Dendrite\11322_plot"
    # brains = os.listdir(path)
    # for brain in brains:
    #     path2 = os.path.join(path,brain)
    #     for name in os.listdir(path2):
    #         print(name)
    #         acro = brain+"_"+name.split("_app2")[0].split("Img_")[-1]
    #         allid = folders[folders_n.index(acro)]
    #         path1 = os.path.join(path2, name)
    #         nt = NeuronTree()
    #         nt.readSwc(path1)
    #         a, d = nt.splitDendriteAxon()
    #         # a.saveObj(os.path.join(r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Model\swc2obj",
    #         #                        '{}_axon.obj'.format(allid)))
    #         d.saveObj(os.path.join(r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Model\swc2obj",
    #                                '{}_den.obj'.format(allid)))

    # three_slice()

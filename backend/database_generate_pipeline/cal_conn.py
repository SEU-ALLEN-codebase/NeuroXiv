#2024/05/03 增加连接强度排序
import pandas as pd

# 加载CSV文件
file_path = r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\all_connection_0501.csv'
df = pd.read_csv(file_path)

# 初始化结果列表
axon_to_dendrites = {}
dendrite_to_axons = {}

# 为每个axon找到相连的dendrite并根据连接强度排序
for axon_idx in range(len(df)):
    axon_name = df.iloc[axon_idx, 0]
    if pd.isnull(axon_name):
        continue
    connected_dendrites = []
    for dendrite_idx in range(1, len(df.columns)):
        dendrite_name = df.columns[dendrite_idx]
        if axon_name == dendrite_name:
            continue
        connection_strength = df.iloc[axon_idx, dendrite_idx]
        if connection_strength > 0:
            connected_dendrites.append((connection_strength, dendrite_name))
    # 按连接强度降序排序，并提取神经元名称
    connected_dendrites.sort(reverse=True, key=lambda x: x[0])
    axon_to_dendrites[axon_name] = ','.join([dendrite for _, dendrite in connected_dendrites])

# 为每个dendrite找到相连的axon并根据连接强度排序
for dendrite_idx, dendrite_name in enumerate(df.columns[1:], 1):
    connected_axons = []
    for axon_idx in range(len(df)):
        axon_name = df.iloc[axon_idx, 0]
        if pd.isnull(axon_name) or dendrite_name == axon_name:
            continue
        connection_strength = df.iloc[axon_idx, dendrite_idx]
        if connection_strength > 0:
            connected_axons.append((connection_strength, axon_name))
    # 按连接强度降序排序，并提取神经元名称
    connected_axons.sort(reverse=True, key=lambda x: x[0])
    dendrite_to_axons[dendrite_name] = ','.join([axon for _, axon in connected_axons])

axon_df = pd.DataFrame.from_dict(axon_to_dendrites, orient='index', columns=['dendrite_ID'])
axon_df.reset_index(inplace=True)
axon_df.rename(columns={'index': 'SWC_Name'}, inplace=True)

dendrite_df = pd.DataFrame.from_dict(dendrite_to_axons, orient='index', columns=['axon_ID'])
dendrite_df.reset_index(inplace=True)
dendrite_df.rename(columns={'index': 'SWC_Name'}, inplace=True)

# 使用“outer”合并确保所有的SWC_Name都被保留
merged_df = pd.merge(dendrite_df, axon_df, on='SWC_Name', how='outer')

# 保存为新的CSV文件
output_file = r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\Connections_CCFv3_final_0503.csv'
merged_df.to_csv(output_file, index=False)

print(f"输出文件已保存为: {output_file}")





# import pandas as pd
#
# # 加载CSV文件
# file_path = r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\all_connection_0501.csv'  # 请替换为您的CSV文件路径
# df = pd.read_csv(file_path)
#
# # 初始化结果列表
# axon_to_dendrites = {}
# dendrite_to_axons = {}
#
# # 确保df的第一行和第一列确实是你想要跳过的标题行和列，如果不是，下面的逻辑需要相应调整
# # 为每个axon找到相连的dendrite
# for axon_idx in range(len(df)):  # 如果第一行不是标题，就不跳过
#     axon_name = df.iloc[axon_idx, 0]  # 获取第一列的axon名称
#     print('axon_name: '+axon_name)
#     if pd.isnull(axon_name):
#         continue  # 如果名称为空，则跳过该行
#     connected_dendrites = []
#     for dendrite_idx in range(1, len(df.columns)):  # 跳过第一列（SWC名称）
#         dendrite_name = df.columns[dendrite_idx]  # 获取dendrite的名称
#         if axon_name == dendrite_name:
#             continue  # 确保axon和dendrite不是同一个
#         cell_value = df.iloc[axon_idx, dendrite_idx]
#         if cell_value > 0:  # 检查是否存在连接
#             connected_dendrites.append(dendrite_name)
#     axon_to_dendrites[axon_name] = ','.join(connected_dendrites)
#
# # 为每个dendrite找到相连的axon
# for dendrite_idx, dendrite_name in enumerate(df.columns[1:], 1):  # 跳过第一列
#     print('dendrite_name: ' + dendrite_name)
#     connected_axons = []
#     for axon_idx in range(len(df)):  # 如果第一行不是标题，就不跳过
#         axon_name = df.iloc[axon_idx, 0]
#         if pd.isnull(axon_name) or dendrite_name == axon_name:
#             continue  # 如果名称为空或者dendrite和axon是同一个，就跳过
#         cell_value = df.iloc[axon_idx, dendrite_idx]
#         if cell_value > 0:
#             connected_axons.append(axon_name)
#     dendrite_to_axons[dendrite_name] = ','.join(connected_axons)
#
# axon_df = pd.DataFrame.from_dict(axon_to_dendrites, orient='index', columns=['dendrite_ID'])
# axon_df.reset_index(inplace=True)
# axon_df.rename(columns={'index': 'SWC_Name'}, inplace=True)
#
# dendrite_df = pd.DataFrame.from_dict(dendrite_to_axons, orient='index', columns=['axon_ID'])
# dendrite_df.reset_index(inplace=True)
# dendrite_df.rename(columns={'index': 'SWC_Name'}, inplace=True)
#
# # 使用“outer”合并确保所有的SWC_Name都被保留
# merged_df = pd.merge(dendrite_df, axon_df, on='SWC_Name', how='outer')
#
# # 保存为新的CSV文件
# output_file = r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\Connections_CCFv3_final_0501.csv'  # 输出文件的名称
# merged_df.to_csv(output_file, index=False)
#
# print(f"输出文件已保存为: {output_file}")


# import pandas as pd
#
# # 加载CSV文件
# file_path = r'D:\NeuroXiv\ALL_DATA_TABLES\NeuroXiv_tables_V20240408\all_connection.csv'  # 请替换为您的CSV文件路径
# df = pd.read_csv(file_path)
#
# # 初始化结果列表和SWC名的集合
# axon_to_dendrites = {}
# dendrite_to_axons = {}
#
# # 为每个axon找到相连的dendrite
# for axon_idx in range(1, len(df)):  # 跳过第一行（SWC名称）
#     axon_name = df.iloc[axon_idx, 0]  # 获取第一列的axon名称
#     connected_dendrites = []
#     for dendrite_idx in range(1, len(df.columns)):  # 跳过第一列（SWC名称）
#         dendrite_name = df.columns[dendrite_idx]  # 获取dendrite的名称
#         # 确保axon和dendrite不是同一个
#         if axon_name != dendrite_name:
#             cell_value = df.iloc[axon_idx, dendrite_idx]
#             # 检查是否存在连接
#             if cell_value > 0:
#                 connected_dendrites.append(dendrite_name)
#     axon_to_dendrites[axon_name] = ','.join(connected_dendrites)
#
# # 为每个dendrite找到相连的axon
# for dendrite_idx, dendrite_name in enumerate(df.columns[1:], 1):  # 跳过第一列
#     connected_axons = []
#     for axon_idx in range(1, len(df)):  # 跳过第一行
#         axon_name = df.iloc[axon_idx, 0]
#         # 确保dendrite和axon不是同一个
#         if dendrite_name != axon_name:
#             cell_value = df.iloc[axon_idx, dendrite_idx]
#             if cell_value > 0:
#                 connected_axons.append(axon_name)
#     dendrite_to_axons[dendrite_name] = ','.join(connected_axons)
#
# axon_df = pd.DataFrame.from_dict(axon_to_dendrites, orient='index', columns=['dendrite_ID'])
# dendrite_df = pd.DataFrame.from_dict(dendrite_to_axons, orient='index', columns=['axon_ID'])
# axon_df.reset_index(inplace=True)
# axon_df.rename(columns={'index': 'SWC_Name'}, inplace=True)
# dendrite_df.reset_index(inplace=True)
# dendrite_df.rename(columns={'index': 'SWC_Name'}, inplace=True)
# merged_df = pd.merge(dendrite_df, axon_df, on='SWC_Name', how='outer')
#
# # 保存为新的CSV文件
# output_file = r'D:\NeuroXiv\ALL_DATA_TABLES\NeuroXiv_tables_V20240408\Connections_CCFv3.csv'  # 输出文件的名称
# merged_df.to_csv(output_file, index=False)
#
# print(f"输出文件已保存为: {output_file}")














# import pandas as pd
#
# # 加载CSV文件
# file_path = r'D:\NeuroXiv\neuroxiv_tables\all_connection_ccfv3.csv'  # 请替换为您的CSV文件路径
# df = pd.read_csv(file_path)
#
#
# # 初始化结果列表和SWC名的集合
# axon_to_dendrites = {}
# dendrite_to_axons = {}
#
# # 为每个axon找到相连的dendrite
# for axon_idx in range(1, len(df)):  # 跳过第一行（SWC名称）
#     axon_name = df.iloc[axon_idx, 0]  # 获取第一列的axon名称
#     print("axon: "+axon_name)
#     connected_dendrites = []
#     for dendrite_idx in range(1, len(df.columns)):  # 跳过第一列（SWC名称）
#         dendrite_name = df.columns[dendrite_idx]  # 获取dendrite的名称
#         cell_value = df.iloc[axon_idx, dendrite_idx]
#         # 检查是否存在连接
#         if cell_value > 0:
#             connected_dendrites.append(dendrite_name)
#     axon_to_dendrites[axon_name] = ','.join(connected_dendrites)
#
# # 为每个dendrite找到相连的axon
# for dendrite_idx, dendrite_name in enumerate(df.columns[1:], 1):  # 跳过第一列
#     print("dendrite: " + dendrite_name)
#     connected_axons = []
#     for axon_idx in range(1, len(df)):  # 跳过第一行
#         axon_name = df.iloc[axon_idx, 0]
#         cell_value = df.iloc[axon_idx, dendrite_idx]
#         if cell_value > 0:
#             connected_axons.append(axon_name)
#     dendrite_to_axons[dendrite_name] = ','.join(connected_axons)
#
#
# axon_df = pd.DataFrame.from_dict(axon_to_dendrites, orient='index', columns=['dendrite_ID'])
# dendrite_df = pd.DataFrame.from_dict(dendrite_to_axons, orient='index', columns=['axon_ID'])
# axon_df.reset_index(inplace=True)
# axon_df.rename(columns={'index': 'SWC_Name'}, inplace=True)
# dendrite_df.reset_index(inplace=True)
# dendrite_df.rename(columns={'index': 'SWC_Name'}, inplace=True)
# merged_df = pd.merge(dendrite_df, axon_df, on='SWC_Name', how='outer')
#
# # # 汇总最终结果到DataFrame
# # results = {'SWC_Name': list(axon_to_dendrites.keys()),
# #            'axon_ID': list(axon_to_dendrites.values()),
# #            'dendrite_ID': list(dendrite_to_axons.values())}
# # results_df = pd.DataFrame(results)
#
# # 保存为新的CSV文件
# output_file = r'D:\NeuroXiv\neuroxiv_tables\Connections_CCFv3_0123.csv'  # 输出文件的名称
# merged_df.to_csv(output_file, index=False)
#
# print(f"输出文件已保存为: {output_file}")











# import concurrent.futures
# import os
# import pickle
# import pandas as pd
# # from sklearn.decomposition import PCA
#
# import matplotlib.pyplot as plt
# import numpy as np
# from basicfunc import *
# from scipy.spatial import distance
# import time
# import sys
#
# # l=int(sys.argv[1])
# # r=int(sys.argv[2])
# from features.utils_fe import NeuronSwc
#
# l = 0
# r = 2743
#
#
# class Neuron():
#     '''
#     return swc: pandas dataframe
#     swc file header: ['id', 'type', 'x', 'y', 'z', 'radius', 'pid']
#     eswc file header: ['id', 'type', 'x', 'y', 'z', 'radius', 'pid', 'seg_id', 'level', 'mode', 'timestamp', 'teraflyindex']
#     soma: type=1 and pid=-1
#     axon arbor : type=2
#     dendritic arbor: type = [3,4]
#     '''
#     SWCHeader = ['id', 'type', 'x', 'y', 'z', 'radius', 'pid']
#     ESWCHeader = ['id', 'type', 'x', 'y', 'z', 'radius', 'pid', 'seg_id', 'level', 'mode', 'timestamp', 'teraflyindex']
#     NeuriteTypes = ['axon', 'dendrite', 'basal', 'apical']
#     NeuColorDict = {'axon': 2, 'dendrite': 3, 'basal': 3, 'apical': 4}
#
#     def __init__(self, path, retype=None, mode=None, scale=1, sep=' ', from_swc=None, prefind=False):
#         self.path = path
#         self.swcname = os.path.split(path)[-1]
#         if from_swc is None:
#             self.df_swc = self.read_swc(self.path, sep=sep)
#             # self.df_swc = self.read_swc(self.path, mode=mode, scale=scale, sep=sep)
#         else:
#             df_swc = pd.DataFrame(from_swc, dtype=np.float32, columns=self.SWCHeader)
#             df_swc[["id", "type", "pid"]] = df_swc[["id", "type", "pid"]].astype(np.int32)
#             self.df_swc = df_swc.copy()
#             # self.df_swc = self.preprocess_swc(from_swc, mode=mode, scale=scale)
#         if scale != 1:
#             self.df_swc = self.swc_scale(scale=scale)
#         if retype is not None:
#             self.df_swc = self.swc_retype(totype=retype)
#         self.swc = self.df_swc.values.tolist()
#         self.length = len(self.swc)
#         self.neurite_types = self.num_of_neurite_type()
#         if mode is not None:
#             if mode.lower() == "all":
#                 self.arbors = [self.to_neurite_type(mode=neutype) for neutype in self.NeuriteTypes]
#             else:
#                 self.df_swc = self.to_neurite_type(mode=mode.lower())
#         if prefind:
#             self.soma, self.bifurs, self.tips = [], [], []
#             if self.length != 0:
#                 self.soma = self.df_swc.loc[self.get_soma(), self.SWCHeader].to_list()
#                 self.bifurs = self.df_swc[self.df_swc['id'].isin(self.get_bifs())].values.tolist()
#                 self.tips = self.df_swc[self.df_swc['id'].isin(self.get_tips())].values.tolist()
#
#     def read_swc(self, file, sep=' ', header=None, skiprows=None):
#         if skiprows is None:
#             with open(file) as f:
#                 rows = f.read().splitlines()
#             skiprows = 0
#             for line in rows:
#                 if line[0] == "#":
#                     skiprows += 1
#                     continue
#                 else:
#                     break
#         swc = pd.read_csv(file, sep=sep, header=None, skiprows=skiprows)
#         if header is None:
#             header = self.SWCHeader
#             if swc.shape[1] >= 12:
#                 header = self.ESWCHeader
#                 for i in np.arange(12, swc.shape[1]):
#                     header.append('fea_' + str(i - 12))
#         if len(header) == swc.shape[1]:
#             swc.columns = header
#         # swc.set_index(['id'], drop=True, inplace=True)
#         return swc
#
#     def save_swc(self, topath, inswc=None, header=None):
#         if inswc is None:
#             inswc = self.df_swc
#         swc = inswc.copy()
#         if header is None:
#             header = self.SWCHeader
#         else:
#             for h in header:
#                 if h not in swc.keys().to_list():
#                     header = swc.keys().to_list()
#                     break
#         # swc.reset_index(inplace=True)
#         header[0] = '##' + header[0]
#         swc.to_csv(topath, sep=' ', index=0, header=header)
#         return True
#
#     def warning_msg(self, msg):
#         print("WARNING: file {0} {1}".format(self.path, msg))
#
#     def to_neurite_type(self, inswc=None, mode=None):
#         '''
#         extract swc arbor :
#             all arbors: mode="all", will return a list of swc_arbors order in ['axon','dendrite','basal','apical']
#             axon: mode="axon"
#             dendrite: mode="dendrite"
#             apical dendrite: mode="apical"
#             basal dendrite: mode="basal"
#         return arbor swc
#         '''
#         if inswc is None:
#             inswc = self.df_swc.copy()
#         if mode is None or mode.lower() not in self.NeuriteTypes:
#             self.warning_msg("Not a registered mode for neurite type: ['axon','dendrite','basal','apical']")
#             return inswc
#         target_types = [2, 3, 4]
#         if mode.lower() == 'axon':
#             target_types = [2]
#         elif mode.lower() == 'dendrite':
#             target_types = [3, 4]
#         elif mode.lower() == 'basal':
#             target_types = [3]
#         elif mode.lower() == 'apical':
#             target_types = [4]
#         somaid = self.get_soma(inswc)
#         # traversal from tip to soma
#         target_tips = self.get_tips(inswc, ntype=target_types)
#         if len(target_tips) == 0:
#             self.warning_msg("No request arbor of " + mode.lower())
#             return inswc
#         swc = inswc.copy()
#         swc.set_index(['id'], drop=True, inplace=True)
#         target_ids = [somaid]
#         for tip in target_tips:
#             sid = tip
#             target_ids.append(sid)
#             spid = sid
#             while True:
#                 spid = swc.loc[sid, 'pid']
#                 if spid == somaid or spid < 0:
#                     break
#                 if spid in swc.index.to_list():
#                     if spid not in target_ids:
#                         target_ids.append(spid)
#                     else:
#                         break
#                 else:
#                     self.warning_msg("Not possible")
#                     break
#                 sid = spid
#         outswc = inswc[inswc.id.isin(target_ids)].copy()
#         return outswc
#
#     def num_of_neurite_type(self, inswc=None):
#         if inswc is None:
#             inswc = self.df_swc.copy()
#         tipids = self.get_tips(inswc)
#         tips = inswc[inswc.id.isin(tipids)].copy()
#         return tips['type'].value_counts().index.tolist()
#
#     def swc_scale(self, inswc=None, scale=1):
#         '''scale the coordinate of swc'''
#         if inswc is None:
#             inswc = self.df_swc.copy()
#         if inswc.shape[0] == 0 or scale == 1:
#             return inswc
#         inswc['x'] *= np.float16(scale)
#         inswc['y'] *= np.float16(scale)
#         inswc['z'] *= np.float16(scale)
#         return inswc
#
#     def swc_retype(self, inswc=None, totype=2, rid=None):
#         '''change type of swc'''
#         if inswc is None:
#             inswc = self.df_swc.copy()
#         if inswc.shape[0] == 0 or totype <= 1:
#             return inswc
#         if rid is None:
#             rid = self.get_soma(inswc)
#         inswc['type'] = totype
#         inswc.loc[rid, 'type'] = 1
#         return inswc
#
#     def get_degree(self, inswc=None):
#         '''区分不同类型的node
#         internode: degree =2
#         tipnode: degree =1
#         bifurcation: degree =3
#         soma node: degree >=3
#         '''
#         if inswc is None:
#             tswc = self.df_swc.copy()
#         else:
#             tswc = inswc.copy()
#         tswc.set_index(['id'], drop=True, inplace=True)
#         tswc['degree'] = tswc['pid'].isin(tswc.index).astype('int')
#         # print(tswc['degree'])
#         n_child = tswc.pid.value_counts()
#         n_child = n_child[n_child.index.isin(tswc.index)]
#         tswc.loc[n_child.index, 'degree'] = tswc.loc[n_child.index, 'degree'] + n_child
#         return tswc
#
#     def get_soma(self, inswc=None):
#         '''return index of soma node in df_swc'''
#         if inswc is None:
#             df = self.df_swc.copy()
#         else:
#             df = inswc.copy()
#         df_soma = df[(df["type"] == 1) & (df["pid"] == -1)].copy()
#         if df_soma.shape[0] == 0:
#             df_soma = df[df["pid"] == -1].copy()
#             if df_soma.shape[0] == 0:
#                 self.warning_msg("No soma (type=1) detected...try to find root(pid=-1)")
#                 self.warning_msg("No soma detected...")
#                 return None
#         if df_soma.shape[0] > 1:
#             self.warning_msg("multiple soma detected.")
#             return None
#         # return df_soma.values[0].tolist()
#         return df_soma.index[0]
#
#     def get_keypoints(self, inswc=None, rid=None):
#         '''
#         Key points: soma,bifurcations,tips
#         return idlist
#         '''
#         if inswc is None:
#             swc = self.df_swc.copy()
#         else:
#             swc = inswc.copy()
#         if rid is None:
#             rid = self.get_soma(inswc)
#         # print(swc.shape)
#         swc = self.get_degree(swc)
#         idlist = swc[((swc.degree != 2) | (swc.index == rid))].index.tolist()
#         return idlist
#
#     def get_tips(self, inswc=None, ntype=None):
#         if inswc is None:
#             swc = self.df_swc.copy()
#         else:
#             swc = inswc.copy()
#         if swc.shape[0] == 0:
#             return None
#         swc = self.get_degree(swc)
#         if ntype is not None:
#             idlist = swc[(swc.degree < 2) & (swc.type.isin(ntype))].index.tolist()
#         else:
#             idlist = swc[(swc.degree < 2)].index.tolist()
#         return idlist
#
#     def get_bifs(self, inswc=None, rid=None, ntype=None):
#         if inswc is None:
#             swc = self.df_swc.copy()
#         else:
#             swc = inswc.copy()
#         if rid is None:
#             rid = self.get_soma(swc)
#         # print(swc.shape)
#         swc = self.get_degree(swc)
#         if ntype is not None:
#             idlist = swc[((swc.degree > 2) & (swc.index != rid) & (swc.type == ntype))].index.tolist()
#         else:
#             idlist = swc[((swc.degree > 2) & (swc.index != rid))].index.tolist()
#         return idlist
#
#     def swc2branches(self, inswc=None):
#         '''
#         reture branch list of a swc
#         branch: down to top
#         '''
#         if inswc is None:
#             inswc = self.df_swc.copy()
#         keyids = self.get_keypoints(inswc)
#         branches = []
#         for key in keyids:
#             if inswc.loc[key, 'pid'] < 0 | inswc.loc[key, 'type'] <= 1:
#                 continue
#             branch = []
#             branch.append(key)
#             pkey = inswc.loc[key, 'pid']
#             while True:
#                 branch.append(pkey)
#                 if pkey in keyids:
#                     break
#                 key = pkey
#                 pkey = inswc.loc[key, 'pid']
#             branches.append(branch)
#         return branches
#
#
# def connectivity(swc_axon: np.array, swc_den: np.array, scale=1):
#     if len(swc_axon) == 0 or len(swc_den) == 0:
#         return None
#     xyz_axon = swc_axon * scale
#     xyz_den = swc_den * scale
#     dist_list = []
#     # t1=time.time()
#     minv = distance.cdist(xyz_axon, xyz_den, 'euclidean')
#     # t2=time.time()
#     # for a_node in xyz_axon:
#     #     for d_node in xyz_den:
#     #         dist_list.append(np.linalg.norm(a_node-d_node, ord=2))
#     # t3=time.time()
#     # print(t2-t1,t3-t2)
#     minvv = np.min(minv)
#
#     return minvv
#
#
# def connectivity2(swc_axon: list, swc_den: list, scale=1 / 25):
#     if not swc_axon or not swc_den:
#         return None
#     xyz_axon = np.array(swc_axon)[:, 2:5] * scale
#     xyz_den = np.array(swc_den)[:, 2:5] * scale
#     # t1 = time.time()
#     xyz_axon_round = np.round(xyz_axon)
#     xyz_axon_round_voxels = set(zip(xyz_axon_round[:, 0], xyz_axon_round[:, 1], xyz_axon_round[:, 2]))
#     xyz_den_round = np.round(xyz_den)
#     xyz_den_round_voxels = set(zip(xyz_den_round[:, 0], xyz_den_round[:, 1], xyz_den_round[:, 2]))
#     emm = xyz_den_round_voxels & xyz_axon_round_voxels
#     # t2 = time.time()
#     # print("regi time ", t2 - t1)
#     if not emm:
#         return None
#
#     dist_list = []
#     # t1 = time.time()
#     minv = distance.cdist(xyz_axon, xyz_den, 'euclidean')
#     # t2 = time.time()
#     # print("calc time ", t2 - t1)
#     minvv = np.min(minv)
#
#     return minvv / scale
#
#
# def connectivity3(swc_axon: list, swc_den_soma: list, medianvalue: float, scale=1):
#     if not swc_axon or not swc_den_soma:
#         return None
#     xyz_axon = np.array(swc_axon)[:, 2:5] * scale
#     xyz_den_soma = np.array([swc_den_soma])[:, 2:5] * scale
#     dist_list = []
#     # t1=time.time()
#     minv = distance.cdist(xyz_axon, xyz_den_soma, 'euclidean')
#     # t2=time.time()
#     # for a_node in xyz_axon:
#     #     for d_node in xyz_den:
#     #         dist_list.append(np.linalg.norm(a_node-d_node, ord=2))
#     # t3=time.time()
#     # print(t2-t1,t3-t2)
#     minvv = np.min(minv)
#
#     return minvv / scale
#
#
# def connectivity_peng(axontips: np.array, swc_den: np.array):
#     if len(axontips) == 0 or len(swc_den) == 0:
#         return None
#     d_mat = distance.cdist(axontips, swc_den, 'euclidean')
#     # print(d_mat.shape)
#     return d_mat
#
#
# def connectivity_jiang(axon_neuron, den_file):
#     # axon_neuron = Neuron(path=axon_file)
#     axon_df = axon_neuron.df_swc
#     xyz_den = np.array(read_swc(den_file))
#     if len(xyz_den) > 0:
#         xyz_den = xyz_den[:, 2:5]
#     else:
#         return 0
#     # xyz_den = np.array([swc_den])[:, 2:5]
#     # get swc_den boundingbox
#     den_xmin = np.min(xyz_den[:, 0])
#     den_xmax = np.max(xyz_den[:, 0])
#     den_ymin = np.min(xyz_den[:, 1])
#     den_ymax = np.max(xyz_den[:, 1])
#     den_zmin = np.min(xyz_den[:, 2])
#     den_zmax = np.max(xyz_den[:, 2])
#     conn_axon_part = axon_df[(axon_df.x >= den_xmin) & (axon_df.x <= den_xmax) &
#                              (axon_df.y >= den_ymin) & (axon_df.y <= den_ymax) &
#                              (axon_df.z >= den_zmin) & (axon_df.z <= den_zmax)].copy()
#     if conn_axon_part.shape[0] > 0:
#         axon_keyps = axon_neuron.get_keypoints()
#         keyp_exist = False
#         for kindex in axon_keyps:
#             if kindex in conn_axon_part.index:
#                 keyp_exist = True
#                 break
#         if not keyp_exist:
#             return 0
#             # pass
#         # get overlap_axon length
#         # axon_segs=[] #list of [id,pid]
#         conn_len = 0
#         for n in conn_axon_part.index:
#             pid = conn_axon_part.loc[n, 'pid']
#             if pid in conn_axon_part['id']:
#                 if conn_axon_part[conn_axon_part.id == pid].shape[0]:
#                     npid = conn_axon_part[conn_axon_part.id == pid].index[0]
#                     conn_len += DISTP(conn_axon_part.loc[n, ['x', 'y', 'z']],
#                                       conn_axon_part.loc[npid, ['x', 'y', 'z']])
#                 # axon_segs.append([nid,pid])
#         # print("Connection strength=", conn_len)
#         return round(conn_len,2)
#     else:
#         return 0
#
#
# def zibei():
#     threshold = 30
#     df = pd.read_csv("hanchuan_method.csv", index_col=0)
#     df_v = df.values
#     prob = np.zeros(df_v.shape)
#     for i in range(df_v.shape[0]):
#         for j in range(df_v.shape[1]):
#             v = np.array(df_v[i, j].split("_"), dtype=float)
#             if len(v) == 0:
#                 final = 0
#             else:
#                 final = np.sum(v <= threshold) / len(v)
#             prob[i, j] = final
#     pd.DataFrame(prob, index=df.index, columns=df.columns).to_csv("hanchuan_method_prob_{}.csv".format(threshold))
#
#
# def DISTP(p1, p2):
#     return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2 + (p1.z - p2.z) ** 2) ** 0.5
#
#
# class NeuronTree():
#     '''
#
#     '''
#
#     def __init__(self) -> None:
#         self.NeuronList = []
#         self.NeuronHash = {}
#         self.indexChildren = []
#         self.path = ""
#         self.binumdict = {}
#         self.distdict = {}
#         self.hahadict = {}
#
#     def initial(self):
#         self.NeuronHash = {}
#         self.indexChildren = []
#         for i in range(0, len(self.NeuronList)):
#             self.NeuronHash[self.NeuronList[i].id] = i
#             self.indexChildren.append([])
#         for i in range(0, len(self.NeuronList)):
#             p = self.NeuronList[i].pid
#             if p == -1:
#                 self.rootidx = i
#                 continue
#             self.indexChildren[self.NeuronHash[p]].append(i)
#
#     def readSwc(self, path):
#         self.path = path
#         with open(self.path, 'r') as f:
#             lines = f.readlines()
#             for line in lines:
#                 if '#' in line:
#                     continue
#                 ss = line.split(' ')
#                 s = NeuronSwc(int(ss[0]),
#                               float(ss[2]), float(ss[3]), float(ss[4]),
#                               int(ss[1]), float(ss[5]), int(ss[6]))
#                 self.NeuronList.append(s)
#         self.initial()
#
#     def toList(self, NL):
#         swclist = []
#         for s in NL:
#             swclist.append([s.id, s.type, s.x, s.y, s.z, s.r, s.pid])
#         return swclist
#
#     def computetree(self):
#         hahadict = {}  # bifurcation index
#         distdict = {}
#         long_p_idx = []
#         bifursidx = [self.rootidx]
#
#         while len(bifursidx):
#             cur_idx = bifursidx.pop()
#             hahadict[cur_idx] = []
#             distdict[cur_idx] = []
#             t = self.indexChildren[cur_idx]
#             for i in range(len(t)):
#                 tmp = t[i]
#                 path = DISTP(self.NeuronList[tmp], self.NeuronList[cur_idx])
#                 while len(self.indexChildren[tmp]) == 1:
#                     ch = self.indexChildren[tmp][0]
#                     path += DISTP(self.NeuronList[tmp], self.NeuronList[ch])
#
#                     tmp = ch
#                 if len(self.indexChildren[tmp]) > 1:
#                     bifursidx.append(tmp)
#                     hahadict[cur_idx].append(tmp)
#                     distdict[cur_idx].append(path)
#
#         binumdict = {}
#         for idx in hahadict:
#             binumdict[idx] = [0] * len(hahadict[idx])
#             for i in range(len(hahadict[idx])):
#                 stack = [hahadict[idx][i]]
#                 while stack:
#                     ch = stack.pop()
#                     binumdict[idx][i] += 1
#                     stack += hahadict[ch]
#
#         # print(binumdict)
#         # print(distdict)
#         # print(hahadict)
#
#         self.binumdict = binumdict
#         self.distdict = distdict
#         self.hahadict = hahadict
#
#     def getlongproj(self):
#         swclist = np.array(self.toList(self.NeuronList))
#         idlist = swclist[:, 0]
#         pidlist = swclist[:, 6]
#         tips = get_tips(swclist.tolist())
#         soma = get_soma(swclist.tolist())
#         bifurs = np.array(get_bifurs(swclist.tolist()))[:, 0]
#         idxlist = []
#         maxpath = -1
#         for tip in tips:
#             passbifur = False
#             tmpidx = []
#             pid = tip[6]
#             id_ = tip[0]
#             idx = np.argwhere(idlist == id_).flatten()[0]
#             tmpidx.append(idx)
#             while True:
#                 idx = np.argwhere(idlist == pid).flatten()
#                 if not idx:
#                     break
#                 idx = idx[0]
#                 id_ = swclist[idx][0]
#                 if not passbifur and id_ in bifurs:
#                     passbifur = True
#                     tmpidx = []
#                 pid = swclist[idx][6]
#                 if id_ == soma[0]:
#                     break
#                 tmpidx.append(idx)
#             if len(tmpidx) > maxpath:
#                 maxpath = len(tmpidx)
#                 idxlist = tmpidx
#
#         return idxlist
#
#     def remove_long_proj(self):
#         threshold = 1000
#         maxbo = 10
#         kdict = {}
#         for k in self.distdict:
#             tmpdist = self.distdict[k]
#             if len(tmpdist) == 2 and max(tmpdist) > threshold and max(self.binumdict[k]) > maxbo:
#                 idx = np.argwhere(np.array(tmpdist) > threshold).flatten()
#                 kdict[k] = np.array(self.hahadict[k])[idx].tolist()
#             elif len(tmpdist) == 1 and max(tmpdist) > threshold and min(self.binumdict[k]) == 0 and max(
#                     self.binumdict[k]) > maxbo:
#                 kdict[k] = self.hahadict[k]
#             # elif
#
#         # print(kdict)
#         rem_idx = []
#         idlist = np.array(self.toList(self.NeuronList))[:, 0]
#         pidlist = np.array(self.toList(self.NeuronList))[:, 6]
#         for k, vlist in kdict.items():
#             for v in vlist:
#                 idx = v
#                 while True:
#                     pid = pidlist[idx]
#                     idx = np.argwhere(idlist == pid).flatten()[0]
#                     if idx == k:
#                         break
#                     rem_idx.append(idx)
#
#         idxlist = self.getlongproj()
#         rem_idx = np.union1d(np.array(rem_idx, dtype='int'), np.array(idxlist, dtype='int'))
#
#         newNL = list(np.delete(np.array(self.NeuronList), rem_idx, axis=0))
#
#         return self.toList(newNL)
#
#
# def process_pair(i, j, ss, at, dendrite_file):
#     # def process_pair(i, j, ss, axon_file, dendrite_file):
#     print("处理轴突: ", i + ss, "和树突: ", j)
#     if i + ss == j:
#         return np.array([])
#
#     # at = np.array(get_tips(read_swc(axon_file)))
#     if len(at) > 0:
#         at = at[:, 2:5]
#
#     d = np.array(read_swc(dendrite_file))
#     if len(d) > 0:
#         d = d[:, 2:5]
#
#     mat = connectivity_peng(at, d)
#
#     if mat is None:
#         return np.array([])
#     else:
#         return np.around(np.min(mat, axis=1), 2).astype(np.float32)
#
#
# def process_pair_jiang(i, j, axon_neu, dendrite_file):
#     print(i ,"-", j)
#
#     mat = connectivity_jiang(axon_neu, dendrite_file)
#     return [os.path.split(dendrite_file)[-1],mat]
#
#
# def main():
#     axonlist = get_path(r"D:\NeuroXiv\Connection\axonpath")
#     denlist = get_path(r"D:\NeuroXiv\Connection\denpath")
#     todir=r"D:\NeuroXiv\Connection\npy"
#     ss = 0
#
#     # 使用 concurrent.futures 处理多进程
#     with concurrent.futures.ProcessPoolExecutor() as executor:
#         for i, axon_file in enumerate(axonlist[ss:], start=ss):\
#
#             futures = []
#             # at = np.array(get_tips(read_swc(axon_file)))
#             axon_neuron=Neuron(axon_file)
#             for j, dendrite_file in enumerate(denlist):
#                 # if os.path.split(axon_file)[-1] == os.path.split(dendrite_file)[-1]:
#                 #     continue
#                 future = executor.submit(process_pair_jiang,i,j, axon_neuron, dendrite_file)
#                 # future = executor.submit(process_pair, i, j, ss, at, dendrite_file)
#                 futures.append(future)
#
#             results=[]
#             for future in concurrent.futures.as_completed(futures):
#                 result = future.result()
#                 # print(i,j,result)
#                 results.append(result)
#             # pickle.dump()
#             this_pf = os.path.join(todir,os.path.split(axon_file)[-1]+".pickle")
#             if not os.path.exists(this_pf):
#                 with open(this_pf, 'wb') as f:
#                     pickle.dump(results, f)
#             # np.save(r"/home/penglab/Data/my_dataserver/NeuroXiv_datasets/Connection/npy/{}.npy".format(i), np.array(futures, dtype=object))
#
#
# if __name__ == "__main__":
#     main()
#     # axonlist = get_path(
#     #     r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Dataset\Raw\unflipped\rawscale_axon_re10") + get_path(
#     #     r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Dataset\Axon_All\1002_Axon_re10") + get_path(
#     #     r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Dataset\Axon_All\ION_Axon_re400")
#     # denlist = get_path(
#     #     r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Dataset\Raw\unflipped\rawscale_dendrite_re4") + get_path(
#     #     r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Dataset\Dendrite\1002_re4") + get_path(
#     #     r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Dataset\Dendrite\11322_re4")
#
#     # axonlist = get_path(r"D:\NeuroXiv\axonpath")
#     # denlist = get_path(r"D:\NeuroXiv\dendritepath")
#     #
#     # axonlist_f = get_path(r"D:\NeuroXiv\axonpath")
#     # denlist_f = get_path(r"D:\NeuroXiv\dendritepath")
#     #
#     # # step 1
#     # # matrix = []
#     # # indx = []
#     # # cols = [os.path.split(x)[-1] for x in denlist]
#     # # start = 2700
#     # # ends = start + 43
#     #
#     # indx = []
#     # cols = []
#     # axontips = []
#     # dens = []
#     # ss = 2600
#     # print(ss)
#     # for x in axonlist[ss:]:
#     #     print(x)
#     #     indx.append(os.path.split(x)[-1])
#     #     tips = np.array(get_tips(read_swc(x)))
#     #     if len(tips) > 0:
#     #         tips = tips[:, 2:5]
#     #     # for i, t in enumerate(tips):
#     #     #     if t[-1] > 25*456./2.:
#     #     #         tips[i, -1] = 25*456.-t[-1]
#     #     axontips.append(tips)
#     #     # print(tips)
#     # # dens = []
#     # for x in denlist[:]:
#     #     print(x)
#     #     d = np.array(read_swc(x))
#     #     if len(d) > 0:
#     #         d = d[:, 2:5]
#     #
#     #     # for i, t in enumerate(d):
#     #     #     if t[-1] > 25*456./2.:
#     #     #         d[i, -1] = 25*456.-t[-1]
#     #
#     #     dens.append(d)
#     #     cols.append(os.path.split(x)[-1])
#     #
#     # # allr = []
#     # for i, at in enumerate(axontips):
#     #     print("axon: ", i + 1 + ss)
#     #     row = []
#     #     for j, d in enumerate(dens):
#     #         # if (j + 1) % 1000 == 0: print(j + 1, end="--")
#     #         # d = np.array(read_swc(dpath))
#     #         # if len(d) > 0:
#     #         #     d = d[:, 2:5]
#     #         if i + ss == j:
#     #             v = np.array([])
#     #             row.append(v)
#     #         else:
#     #             nat = np.array(at)
#     #             mat = connectivity_peng(nat, d)
#     #
#     #             if mat is None:
#     #                 v = np.array([])
#     #             else:
#     #                 v = np.around(np.min(mat, axis=1), 2).astype(np.float32)
#     #             row.append(v)
#     #     # allr.append(row)
#     #     # print()
#     #     np.save(r"./hcm_npy_nonflip/hanchuan_method_{}.npy".format(i + ss + 1),
#     #             np.array(row, dtype=object))
#
#     # step 2
#     # path = r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Scripts\hcm_npy_nonflip"
#     # hcm = ["hanchuan_method_" + str(x + 1) + ".npy" for x in range(0, 2743)]
#     # threshold = 30
#     # emm = []
#     # for file in hcm:
#     #     vs = np.load(os.path.join(path, file), allow_pickle=True)
#     #     gaga = []
#     #     for v in vs:
#     #         fz = np.sum(v <= threshold)
#     #         fm = len(v)
#     #         if fm == 0:
#     #             final = 0
#     #         else:
#     #             final = np.float32(fz / fm)
#     #         gaga.append(final)
#     #     print(file)
#     #     emm.append(gaga)
#     # pd.DataFrame(emm, index=cols[:2743], columns=cols).to_csv(
#     #     "affinity_map_nonflip_thres{}_20211230.csv".format(threshold))

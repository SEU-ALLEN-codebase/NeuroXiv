import os
import json
import numpy as np
import pandas as pd


def create_conn_json():
    axon = {}
    dendrite = {}

    df = pd.read_csv(r"D:\ZhixiYun\Projects\Neuron_Morphology_Table\Scripts\test1_2743_filter8.csv", index_col=0)
    dfnodes = list(pd.read_csv(r"D:\ZhixiYun\Projects\Neuron_Morphology_Table\Scripts\nodes_8.csv", index_col=0).index)
    df.index = dfnodes[:2743]
    df.columns = dfnodes

    for i in range(df.shape[0]):
        a = df.index[i]
        print(i)
        for j in range(df.shape[1]):
            d = df.columns[j]
            v = df.iloc[i, j]
            if not np.isnan(v):
                if a not in axon:
                    axon[a] = []
                if d not in dendrite:
                    dendrite[d] = []
                axon[a].append(d)
                dendrite[d].append(a)
    with open("conn.json", "w") as f:
        json.dump({"axon": axon, "dendrite": dendrite}, f, indent=4)
    return


def create_RenderTree_json():
    with open(r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Tables\tree.json") as f:
        tree = json.load(f)
    vtkfiles = os.listdir(r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Model\surf\vtk")
    vtkfiles_n = [
        x.replace(".vtk", "").replace("_", "/").replace("CUL4//5", "CUL4, 5").replace("fiber/tracts", "fiber tracts")
        for x in vtkfiles]
    banames = [x['acronym'] for x in tree]
    sort_idx = []
    for ba in vtkfiles_n:
        idx = np.argwhere(np.array(vtkfiles_n) == ba).flatten()
        if len(idx) == 0:
            continue
        sort_idx.append(idx[0])

    iddict = {}
    a = 1
    idtreedict = {}
    for t in tree:
        iddict[t['id']] = t['structure_id_path']
        idtreedict[t['id']] = t
        idtreedict[t['id']]['src'] = None
        idtreedict[t['id']]['disabled'] = True
        # idtreedict[t['id']]['visible'] = False
        idtreedict[t['id']]['children'] = []
        a = max(a, len(t['structure_id_path']))

    # print(iddict)
    sbdict = {997: [0]}
    ididxdict = {997: 0}
    idxall = [1] + [0] * (a - 1)
    orderdict = {}
    for k in iddict:
        if k == 997:
            continue
        sid = iddict[k]
        for i in range(len(sid)):
            if sid[i] == k:
                if idxall[i] == 0:
                    if sid[-2] not in ididxdict:
                        ididxdict[sid[-2]] = 0
                    idxlist = sbdict[sid[i - 1]] + [ididxdict[sid[-2]]]
                    ididxdict[sid[-2]] += 1
                    break
                else:
                    idxlist = sbdict[sid[i - 1]] + [ididxdict[sid[-2]]]
                    ididxdict[sid[-2]] += 1

        sbdict[k] = idxlist
    print(sbdict)

    yzxdict = {'children': []}
    for k in sbdict:
        print(k)
        idxlist = sbdict[k]
        tmpdict = yzxdict
        for i, idx in enumerate(idxlist):
            if i == len(idxlist) - 1:
                aa = idtreedict[k]
                del aa['graph_id']
                del aa['graph_order']
                del aa['structure_id_path']
                del aa['structure_set_ids']
                iidx = np.argwhere(np.array(vtkfiles_n) == aa['acronym']).flatten()
                if len(iidx) > 0:
                    iidx = iidx[0]
                    aa['src'] = '/data/surf/vtk/' + vtkfiles[iidx]
                    aa['disabled'] = False
                    # aa['visible'] = False
                else:
                    aa['src'] = None
                    aa['disabled'] = True
                    # aa['visible'] = False

                tmpdict['children'].append(aa)

            else:
                # print(i,idx,tmpdict)
                tmpdict = tmpdict['children'][idx]
            # print(i,idx,tmpdict)
    # print(yzxdict)
    with open("./surf_tree.json", 'w') as f:
        json.dump(yzxdict['children'], f, indent=4)
    # print(max(sbdict.keys()),min(sbdict.keys()), len(sbdict))


if __name__ == "__main__":
    create_RenderTree_json()

    # create_conn_json()
    # with open("querry.json") as f:
    #     a = json.load(f)
    # print(a["children"][0]["children"][1]["candidates"])
    #
    # df_CT1 = pd.read_csv(r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Tables\CellType\2743_CellType.csv", index_col=0)
    # df_CT1.index = [x.split(".")[0] for x in df_CT1.index]
    #
    # df_CT2 = pd.read_csv(r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Tables\CellType\11322_CellType_Detail.csv", index_col=0)
    # df_CT2.index = [str(df_CT2.loc[x]["BrainID"]) + "_" + x.split("Img_")[1].split("_app2")[0] for x in df_CT2.index]
    #
    # df_CT = pd.concat([df_CT1,df_CT2])
    #
    # with open(r"E:\ZhixiYun\Projects\Neuron_Morphology_Table\Scripts\neuron_code\neuron\tree.json") as f:
    #     tree = json.load(f)
    # cortex = []
    # sortedct = []
    # ctlist = df_CT["CellType"].tolist()
    # for node in tree:
    #     for ct in ctlist:
    #         if ct == node["acronym"]:
    #             sortedct.append(ct)
    #             break
    # print(np.setdiff1d(ctlist, sortedct))
    #
    # if 315 in node['structure_id_path']:
    #     cortex.append(node['acronym'])
    # print(sortedct)

    # emm = [
    #     "FRP",
    #     "FRP1", "FRP5",
    #     "FRP6a", "MOp", "MOp1", "MOp2/3", "MOp5", "MOp6", "MOp6a", "MOp6b",
    #     "MOs",
    #     "MOs1", "MOs2/3",
    #     "MOs5",
    #     "MOs6", "MOs6a",
    #     "MOs6b",
    #     "SSp6", "SSp-n",
    #     "SSp-n1",
    #     "SSp-n2/3", "SSp-n4", "SSp-n5",
    #     "SSp-n6",
    #     "SSp-n6a",
    #     "SSp-n6b",
    #     "SSp-bfd", "SSp-bfd1",
    #     "SSp-bfd2/3", "SSp-bfd4",
    #     "SSp-bfd5",
    #     "SSp-bfd6", "SSp-bfd6a",
    #     "SSp-bfd6b",
    #     "SSp-ll", "SSp-ll1",
    #     "SSp-ll2/3",
    #     "SSp-ll4",
    #     "SSp-ll5",
    #     "SSp-ll6",
    #     "SSp-ll6a",
    #     "SSp-m",
    #     "SSp-m1",
    #     "SSp-m2/3",
    #     "SSp-m4",
    #     "SSp-m5",
    #     "SSp-m6",
    #     "SSp-m6a",
    #     "SSp-m6b",
    #     "SSp-ul",
    #     "SSp-ul1",
    #     "SSp-ul2/3", "SSp-ul4",
    #     "SSp-ul5",
    #     "SSp-ul6a",
    #     "SSp-tr",
    #     "SSp-tr1",
    #     "SSp-tr2/3", "SSp-tr4",
    #     "SSp-tr5",
    #     "SSp-tr6a",
    #     "SSp-un", "SSp-un1",
    #     "SSp-un2/3",
    #     "SSp-un4",
    #     "SSp-un5",
    #     "SSp-un6",
    #     "SSp-un6a",
    #     "SSp-un6b",
    #     "SSs",
    #     "SSs1",
    #     "SSs2/3",
    #     "SSs4", "SSs5",
    #     "SSs6",
    #     "SSs6a",
    #     "SSs6b",
    #     "GU1",
    #     "GU2/3",
    #     "GU4",
    #     "GU5",
    #     "GU6",
    #     "GU6a", "GU6b",
    #     "VISC1",
    #     "VISC2/3",
    #     "VISC4",
    #     "VISC5",
    #     "VISC6",
    #     "VISC6a",
    #     "VISC6b",
    #     "AUDd1",
    #     "AUDd2/3",
    #     "AUDd4",
    #     "AUDd5",
    #     "AUDd6",
    #     "AUDd6a",
    #     "AUDp",
    #     "AUDp1",
    #     "AUDp2/3",
    #     "AUDp4",
    #     "AUDp5",
    #     "AUDp6",
    #     "AUDp6a",
    #     "AUDpo1",
    #     "AUDpo2/3",
    #     "AUDpo4",
    #     "AUDpo5",
    #     "AUDpo6",
    #     "AUDv",
    #     "AUDv1",
    #     "AUDv2/3",
    #     "AUDv4",
    #     "AUDv5",
    #     "AUDv6",
    #     "AUDv6a",
    #     "VISal",
    #     "VISal1",
    #     "VISal2/3",
    #     "VISal4",
    #     "VISal5",
    #     "VISal6",
    #     "VISal6a",
    #     "VISam",
    #     "VISam2/3",
    #     "VISam4",
    #     "VISam5",
    #     "VISam6a",
    #     "VISl",
    #     "VISl1",
    #     "VISl2/3",
    #     "VISl4",
    #     "VISl5",
    #     "VISl6",
    #     "VISl6a",
    #     "VISl6b",
    #     "VISp",
    #     "VISp1",
    #     "VISp2/3",
    #     "VISp4",
    #     "VISp5",
    #     "VISp6",
    #     "VISp6a",
    #     "VISp6b",
    #     "VISpl1",
    #     "VISpl2/3",
    #     "VISpl4",
    #     "VISpl5",
    #     "VISpl6a",
    #     "VISpm",
    #     "VISpm1",
    #     "VISpm2/3",
    #     "VISpm4",
    #     "VISpm5",
    #     "VISpm6a",
    #     "VISli",
    #     "VISli1",
    #     "VISli2/3",
    #     "VISli4",
    #     "VISli5",
    #     "VISli6a",
    #     "VISpor",
    #     "VISpor1",
    #     "VISpor2/3",
    #     "VISpor4",
    #     "VISpor5",
    #     "VISpor6a",
    #     "ACAd1",
    #     "ACAd2/3",
    #     "ACAd5",
    #     "ACAd6",
    #     "ACAd6a",
    #     "ACAv",
    #     "ACAv1",
    #     "ACAv2/3",
    #     "ACAv5",
    #     "ACAv6a",
    #     "PL1",
    #     "PL2/3",
    #     "PL5",
    #     "PL6a",
    #     "ILA2/3",
    #     "ILA5",
    #     "ORBl1",
    #     "ORBl2/3",
    #     "ORBl5",
    #     "ORBl6",
    #     "ORBl6a",
    #     "ORBl6b",
    #     "ORBm1",
    #     "ORBm2/3",
    #     "ORBm5",
    #     "ORBvl1",
    #     "ORBvl2/3",
    #     "ORBvl5",
    #     "ORBvl6a",
    #     "AId1",
    #     "AId2/3",
    #     "AId5",
    #     "AId6",
    #     "AId6a",
    #     "AId6b",
    #     "AIp1",
    #     "AIp2/3",
    #     "AIp5",
    #     "AIp6",
    #     "AIp6a",
    #     "AIv",
    #     "AIv1",
    #     "AIv2/3",
    #     "AIv5",
    #     "AIv6a",
    #     "RSPagl",
    #     "RSPagl1",
    #     "RSPagl2/3",
    #     "RSPagl5",
    #     "RSPagl6a",
    #     "RSPd",
    #     "RSPd1",
    #     "RSPd2/3",
    #     "RSPd5",
    #     "RSPd6a",
    #     "RSPv",
    #     "RSPv1",
    #     "RSPv2/3",
    #     "RSPv5",
    #     "RSPv6a",
    #     "VISa",
    #     "VISa1",
    #     "VISa2/3",
    #     "VISa4",
    #     "VISa5",
    #     "VISrl",
    #     "VISrl1",
    #     "VISrl2/3",
    #     "VISrl4",
    #     "VISrl5",
    #     "VISrl6",
    #     "VISrl6a",
    #     "TEa",
    #     "TEa1",
    #     "TEa2/3",
    #     "TEa4",
    #     "TEa5",
    #     "TEa6",
    #     "TEa6a",
    #     "PERI2/3",
    #     "PERI5",
    #     "PERI6a",
    #     "ECT1",
    #     "ECT2/3",
    #     "ECT5",
    #     "ECT6",
    #     "ECT6a",
    #     "ECT6b",
    #     'MOB', 'AOB', 'AON', 'TT', 'DP', 'PIR', 'NLOT', 'COAa', 'COAp', 'PAA', 'TR', 'HPF', 'CA1', 'CA2', 'CA3', 'DG',
    #     'IG', 'ENTl', 'ENTm', 'PAR', 'POST', 'PRE', 'SUB', 'ProS', 'HATA', 'APr', 'CLA', 'EPd', 'EPv', 'LA', 'BLA',
    #     'BMA', 'PA', 'CP', 'ACB', 'FS', 'OT', 'LSc', 'LSr', 'LSv', 'SF', 'AAA', 'CEA', 'IA', 'MEA', 'PAL', 'GPe', 'SI',
    #     'MA', 'MS', 'NDB', 'TRS', 'BST', 'BS', 'TH', 'VAL', 'VM', 'VPL', 'VPLpc', 'VPM', 'VPMpc', 'PoT', 'SPFp', 'PP',
    #     'MG', 'LGd', 'LP', 'PO', 'POL', 'SGN', 'AV', 'AM', 'AD', 'IAD', 'LD', 'IMD', 'MD', 'SMT', 'PR', 'PVT', 'PT',
    #     'RE', 'Xi', 'CM', 'PCN', 'CL', 'PF', 'PIL', 'RT', 'IGL', 'LGv', 'HY', 'PVH', 'PVi', 'ARH', 'DMH', 'MPO', 'SBPV',
    #     'SCH', 'AHN', 'MM', 'SUM', 'TMv', 'MPN', 'PMd', 'VMH', 'PH', 'LHA', 'LPO', 'PSTN', 'PeF', 'TU', 'ZI', 'MB',
    #     'SCs', 'IC', 'SNr', 'VTA', 'MRN', 'SCm', 'PAG', 'APN', 'NOT', 'NPC', 'PPT', 'CUN', 'RN', 'AT', 'PPN', 'IPN',
    #     'DR', 'P', 'NLL', 'PSV', 'PB', 'SOC', 'B', 'PCG', 'PG', 'PRNc', 'SUT', 'TRN', 'V', 'P5', 'CS', 'LDT', 'NI',
    #     'PRNr', 'MY', 'DCO', 'VCO', 'CU', 'SPVC', 'SPVI', 'DMX', 'GRN', 'IO', 'IRN', 'LRN', 'MARN', 'MDRN', 'MDRNd',
    #     'MDRNv', 'PARN', 'PGRNl', 'PRP', 'PPY', 'LAV', 'MV', 'SPIV', 'SUV', 'RM', 'CENT', 'CUL', 'DEC', 'FOTU', 'PYR',
    #     'UVU', 'NOD', 'SIM', 'AN', 'PRM', 'COPY', 'PFL', 'FL', 'FN', 'fiber tracts', 'mlf', 'll', 'arb', 'fa', 'ccg',
    #     'fp', 'ccb', 'int', 'or', 'nst', 'tspc', 'cing', 'alv', 'fi', 'fx', 'dhc', 'mfb', 'pm', 'mtt', 'sm', 'fr',
    #     'CUL4 5',
    #     "Mmd",
    #     "Mml",
    #     "Mmme",
    #     "unknown"
    # ]
    # print(emm[0:256])
    # for i in range(0, 256):
    #     ct = emm[i]
    #     if ct.endswith("1"):
    #         layer = "1"
    #         ct = ct[:-1] + " Layer1"
    #     elif ct.endswith("2/3"):
    #         layer = "2/3"
    #         ct = ct[:-3] + " Layer2/3"
    #     elif ct.endswith("4"):
    #         layer = "4"
    #         ct = ct[:-1] + " Layer4"
    #     elif ct.endswith("5"):
    #         layer = "5"
    #         ct = ct[:-1] + " Layer5"
    #     elif ct.endswith("6"):
    #         layer = "6"
    #         ct = ct[:-1] + " Layer6"
    #     elif ct.endswith("6a"):
    #         layer = "6a"
    #         ct = ct[:-2] + " Layer6a"
    #     elif ct.endswith("6b"):
    #         layer = "6b"
    #         ct = ct[:-2] + " Layer6b"
    #
    #     emm[i] = ct
    # a["children"][0]["children"][1]["candidates"] = emm
    # with open("querry.json", "w") as f:
    #     json.dump(a, f, indent=4)

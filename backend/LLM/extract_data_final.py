import numpy as np
import pandas as pd
import random


# input: id-list
# step1: overview#1
def global_info_text_v2(indf):
    '''
    indf: all_info_table
    used keys: ['data_source','celltype','layer','has_recon_axon','has_recon_den','has_apical','has_local','hemisphere']
    '''
    ds = indf["data_source"].value_counts()
    total_num = indf.shape[0]
    outtext = 'The queried data comprises ' + str(total_num) + ' neurons extracted from ' + str(
        ds.shape[0]) + ' datasets: '
    for i, d in enumerate(ds.index):
        if i == 0:
            outtext += (d + ' (' + str(int(ds[d])) + ' neurons)')
        elif i > 0 and i < ds.shape[0] - 1:
            outtext += (', ' + d + ' (' + str(int(ds[d])) + ' neurons)')
        else:
            outtext += (' and ' + d + ' (' + str(int(ds[d])) + ' neurons)')
    outtext += '.'
    # ns=indf["data_source"].value_counts()
    # 有多少个 structures
    axon_num = indf[indf['has_recon_axon'] == '1'].shape[0]
    den_num = indf[indf['has_recon_den'] == '1'].shape[0]
    apical_num = indf[indf['has_apical'] == '1'].shape[0]
    local_num = indf[indf['has_local'] == '1'].shape[0]
    outtext += f" This selection encompasses neuron structures, including axons ({axon_num}), basal dendrites ({den_num}), apical dendrites ({apical_num}), and local dendrites ({local_num})."
    # hemisphere
    lefth = indf[indf['hemisphere'] == "Left"].shape[0]
    righth = indf[indf['hemisphere'] == "Right"].shape[0]
    outtext += f" The queried data locates in left hemisphere ({lefth}) and right hemisphere ({righth})."
    cts_num = indf['celltype'].value_counts().shape[0]
    outtext += f" The queried data is distributed across {cts_num} brain regions, detailed as follows: "
    cts = indf['celltype'].value_counts()
    for i, ct in enumerate(cts.index):
        ctn = str(int(cts[ct]))
        if i == 0:
            outtext += (f" {ct} ({ctn} neurons)")
        elif i > 0 and i < cts_num - 1:
            outtext += (f", {ct} ({ctn} neurons)")
        else:
            outtext += (f", and {ct} ({ctn} neurons)")
    outtext += '. '
    indf['layer'].value_counts()
    layer_num = indf['layer'].value_counts().sum()
    if layer_num > 0:
        outtext += f"Specifically, there are {layer_num} neurons in cortical layers, including "
        layers = indf['layer'].value_counts()
        for i, l in enumerate(layers.index):
            ctn = int(layers[l])
            if i == 0:
                outtext += (f" {l} ({ctn} neurons)")
            elif i > 0 and i < layers.shape[0] - 1:
                outtext += (f", {l} ({ctn} neurons)")
            else:
                outtext += (f", and {l} ({ctn} neurons)")
        outtext += '.'
    return outtext


def fea2text_v2(indf, feadf, axonfea=True, detail_types=2,
                fealist=['Total Length', 'Max Path Distance', 'Number of Bifurcations', 'Center Shift']):
    outtext = ""
    usedfeas = feadf.keys()
    if fealist is not None:
        usedfeas = fealist
    ds = indf["data_source"].value_counts()
    for s in ds.index:
        sdf = indf[indf['data_source'] == s].copy()
        sdf_types = indf['celltype'].value_counts()
        for i, t in enumerate(sdf_types.index):
            if i >= detail_types:
                break
            ndf = sdf[(sdf.celltype == t)].index
            if not axonfea:
                ndf = sdf[(sdf.celltype == t) & (sdf.has_recon_den == '1')].index
            if len(ndf) <= 1:
                continue
            if axonfea:
                outtext += f"The axonal arbor data ({t} neurons) obtained from the {s} source reveals the following statistics:\n"
                for f, fea in enumerate(usedfeas):
                    fmean = feadf.loc[ndf, 'morpho_axon_'+fea.lower()].mean()
                    fmean = round(fmean, 2)
                    fstd = feadf.loc[ndf, 'morpho_axon_'+fea.lower()].std()
                    fstd = round(fstd, 2)
                    if f < 2:
                        outtext += f"- '{fea}': the mean value is {fmean} μm with a standard deviation of {fstd} μm."
                        outtext += '\n'
                    elif f == 2:
                        outtext += f"- '{fea}': the mean value is {fmean} with a standard deviation of {fstd}."
                        outtext += '\n'
                    else:
                        outtext += f"- '{fea}': the mean value is {fmean} with a standard deviation of {fstd}"
            else:
                outtext += f"The dendritic arbor data ({t} neurons) obtained from the {s} source reveals the following statistics:\n"
                for f, fea in enumerate(usedfeas):
                    fmean = feadf.loc[ndf, 'morpho_den_'+fea.lower()].mean()
                    fmean = round(fmean, 2)
                    fstd = feadf.loc[ndf, 'morpho_den_'+fea.lower()].std()
                    fstd = round(fstd, 2)
                    if f < 2:
                        outtext += f"- '{fea}': the mean value is {fmean} μm with a standard deviation of {fstd} μm."
                        outtext += '\n'
                    elif f == 2:
                        outtext += f"- '{fea}': the mean value is {fmean} with a standard deviation of {fstd}."
                        outtext += '\n'
                    else:
                        outtext += f"- '{fea}': the mean value is {fmean} with a standard deviation of {fstd}"
            outtext += '\n'
    return outtext


def proj_patterns_v2(indf, feadf, axonfea=True, detail_types=2):
    layer_list = ['L1', 'L2', 'L2/3', 'L4', 'L5', 'L6a', 'L6b']
    outtext = ""
    ds = indf["data_source"].value_counts()
    # print(ds)
    for s in ds.index:
        # print(s)
        sdf = indf[indf['data_source'] == s].copy()
        sdf_types = indf['celltype'].value_counts()
        for i, t in enumerate(sdf_types.index):
            if i >= detail_types:
                break
            ndf = sdf[(sdf.celltype == t)].index
            if not axonfea:
                ndf = sdf[(sdf.celltype == t) & (sdf.has_recon_den == '1')].index
            if len(ndf) <= 1:
                continue
            proj_matrix = feadf.loc[ndf, :].mean()
            if axonfea:
                outtext += f"The axonal arbor data ({t} neurons) obtained from the {s} source reveals the following arborized patterns:"
            else:
                outtext += f"The dendritic arbor data ({t} neurons) obtained from the {s} source reveals the following arborized patterns:"
            outtext += "\n(The format is as follows: brain region name is listed in descending order of length, along with the proportion of arborized length within that brain region.)\n"
            relaproj = []
            # print(proj_matrix.index[0])
            for r in proj_matrix.index:
                if (r.split('_')[-1] == 'abs') or proj_matrix[r] == 0 or (r.split('_')[-2] in layer_list):
                    continue
                if axonfea:
                    if proj_matrix['proj_axon_' + r.split('_')[-2] + '_abs'] > 1000:
                        relaproj.append(r)
                else:
                    if proj_matrix['proj_den_' + r.split('_')[-2] + '_abs'] > 1000:
                        relaproj.append(r)
            projpatterns = proj_matrix[relaproj].sort_values(ascending=False)
            for r in projpatterns.index:
                rname = r.split('_')[-2]
                if rname == 'fiber tracts':
                    continue
                if axonfea:
                    pl = str(round(proj_matrix['proj_axon_' + r.split('_')[-2] + '_abs'], 1))
                else:
                    pl = str(round(proj_matrix['proj_den_' + r.split('_')[-2] + '_abs'], 1))
                pr = str(round(proj_matrix[r] * 100, 1))
                outtext += f"- {rname}: {pl} μm ({pr}%)."
                outtext += '\n'
                # outtext+=('- projected region'+rname+':'+str(round(proj_matrix['proj_axon_'+r.split('_')[-2]+'_abs'],1))+'um ('+str(round(proj_matrix[r]*100,1))+'%)\n')
    outtext += '\n'
    return outtext


def initalInput():
    info_file = './dbtables/ana_used_neurons.csv'
    axonfea_file = './dbtables/axonfull_morpho.csv'
    denfea_file = './dbtables/denfull_morpho.csv'
    axonproj_file = './dbtables/Proj_Axon_Final.csv'
    denproj_file = './dbtables/Proj_Den_Final.csv'
    allneus = pd.read_csv(info_file, index_col=['ID'], low_memory=False)
    axonfeas = pd.read_csv(axonfea_file, index_col=['ID'])
    denfeas = pd.read_csv(denfea_file, index_col=['ID'])
    axonproj = pd.read_csv(axonproj_file, index_col=['ID'])
    denproj = pd.read_csv(denproj_file, index_col=['ID'])
    ccf_neus = allneus[(allneus.brain_atlas == "CCFv3") & (allneus.has_local == 0)].copy()

    inlist = random.choices(ccf_neus.index.to_list(), k=150)
    print('inlist:')
    print(inlist)
    ana_neus = ccf_neus.loc[inlist, :].copy()
    origin_basic = global_info_text_v2(ana_neus)
    origin_fea_den = fea2text_v2(ana_neus, denfeas, axonfea=False)
    origin_fea_axon = fea2text_v2(ana_neus, axonfeas)
    origin_proj_axon = proj_patterns_v2(ana_neus, axonproj)
    origin_proj_den = proj_patterns_v2(ana_neus, denproj, axonfea=False)
    print(origin_fea_den + origin_fea_axon)
    return origin_basic, origin_fea_den, origin_fea_axon, origin_proj_den, origin_proj_axon


if __name__ == '__main__':
    initalInput()

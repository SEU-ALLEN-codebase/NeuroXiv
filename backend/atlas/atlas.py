import path, sys

cur_path = path.Path(__file__).abspath()
api_dir = cur_path.parent.parent
project_dir = api_dir.parent
print(api_dir, project_dir)
sys.path.append(api_dir)
# print(folder.parent.parent)
# print(sys.path)
import numpy as np
from database import DB
import json
# import database
import os

# PATH_ROOT = "D:/NeuroXiv"
# api_dir = r"D:\zx\tencent\data\database\20220113"
# myDB = DB(os.path.join(api_dir, "test.db"))

myDB = DB(os.path.join(api_dir, "database/test_0410.db"))


# 获取所有species信息
def get_all_species():
    tmp_dict = myDB.queryall('''SELECT id, name FROM SPECIES''')
    if tmp_dict is None:
        return None
    print(tmp_dict)
    species = []
    for id, name in zip(tmp_dict['ID'], tmp_dict['name']):
        species.append({"id": id, "name": name})
    print(species)
    return species


# 根据species id获取species信息，详情见api文档
def get_species_info(species_id):
    SQL = '''SELECT id, * FROM Species WHERE id = '{}' limit 1;'''.format(species_id)
    species_dict = myDB.queryall(SQL)
    if species_dict is None or species_dict == {}:
        return None
    print(species_dict)
    ontology_id = species_dict['ontology_id']
    SQL = '''SELECT id, * FROM Atlas WHERE id = '{}' limit 1;'''.format(ontology_id)
    atlas_dict = myDB.queryall(SQL)
    if atlas_dict is None or atlas_dict == {}:
        return None
    print(atlas_dict)
    image_list_str = species_dict['image_list']
    image_list = []
    if image_list_str != 'nan':
        image_list_tmp = image_list_str.split(',')
        image_list = [{'image_type': image_type} for image_type in image_list_tmp]

    species_info = {
        'id': species_dict['ID'],
        'name': species_dict['name'],
        'atlas': {
            'id': atlas_dict['ID'],
            'name': atlas_dict['name']
        },
        'zslice_number': species_dict['zslice_number'],
        'image_list': image_list,
        'has_svg': True if species_dict['has_svg'] else False,
        'width': species_dict['width'],
        'height': species_dict['height']
    }
    print(species_info)
    return species_info


# 根据species id和image type，获取某一张zslice的图片相关信息，详情见api文档
def get_image(species_id, image_type, zslice):
    SQL = '''SELECT id, * FROM Species WHERE id = '{}' limit 1;'''.format(species_id)
    species_dict = myDB.queryall(SQL)
    if species_dict is None or species_dict == {}:
        return None
    print(species_dict)

    matrix_set_path = species_dict['matrix_set_path']
    # with open(os.path.join(project_dir, matrix_set_path), 'r') as f:
    with open(matrix_set_path, 'r') as f:
        matrix_set_config = json.load(f)
    # print(matrix_set_config) 

    image_info = {
        'id': species_dict['ID'],
        'name': species_dict['name'],
        'source': {
            'url': species_dict['url'],
            'layer': species_dict['layer_name'] + '_' + str(zslice) + '_' + image_type,
            'matrix_set': species_dict['matrix_set_name'],
            'matrix_ids': matrix_set_config['matrix_ids'],
            'resolutions': matrix_set_config['resolutions'],
            'extent': matrix_set_config['extent']
        },
        'width': species_dict['width'],
        'height': species_dict['height']
    }

    print(image_info)
    return image_info


# 根据species id和image type获取对应的缩略图列表的信息，详情见api文档
def get_thumbnail_list(species_id, image_type):
    SQL = '''SELECT id, * FROM Species WHERE id = '{}' limit 1;'''.format(species_id)
    species_dict = myDB.queryall(SQL)
    if species_dict is None or species_dict == {}:
        return None
    print(species_dict)
    # SQL = '''SELECT * FROM Species_image WHERE species_id = '{}' AND image_type = '{}' limit 1;'''.format(species_id, image_type)
    SQL = '''SELECT * FROM Species_image WHERE species_id = ? AND image_type = ? limit 1;'''
    # print(SQL)
    # image_dict = myDB.queryall(SQL)
    image_dict = myDB.queryall(SQL, (species_id, image_type,))
    if image_dict is None or image_dict == {}:
        return None
    print(image_dict)

    # thumbnail_dir_path = image_dict['thumbnail_dir_path']
    # type_image_dir_path_list = os.listdir(os.path.join(project_dir, thumbnail_dir_path))

    # thumbnail_dir_path = os.path.join(project_dir, image_dict['thumbnail_dir_path'])
    thumbnail_dir_path = image_dict['thumbnail_dir_path']
    type_image_dir_path_list = os.listdir(thumbnail_dir_path)

    thumbnail_info = {
        'id': species_dict['ID'],
        'name': species_dict['name'],
        'thumbnail': [],
        'zslice_number': species_dict['zslice_number']
    }

    thumbnail = []
    for file_name in type_image_dir_path_list:
        file_name_parts = file_name.split('_')[1]  # 这将给出 '1.jpg'
        number_part = file_name_parts.split('.')[0]  # 这将给出 '1'
        zslice = int(number_part) + 1  # 现在它将成功地将 '1' 转换为整数
        thumbnail.append({
            'src': (os.path.join(image_dict['thumbnail_dir_path'], file_name)).replace("\\","/"),
            'zslice': zslice
        })
    thumbnail.sort(key=lambda x: x['zslice'])
    thumbnail_info['thumbnail'] = thumbnail
    print(thumbnail_info)
    return thumbnail_info


# 根据atlas id获取该atlas的脑区树状结构
def get_structural_ontology(atlas_id):
    SQL = '''SELECT id, * FROM Atlas WHERE id = '{}' limit 1;'''.format(atlas_id)
    atlas_dict = myDB.queryall(SQL)
    if atlas_dict is None or atlas_dict == {}:
        return None
    print(atlas_dict)
    # structural_ontology_path = os.path.join(project_dir, atlas_dict['structural_ontology_path'])
    structural_ontology_path = atlas_dict['structural_ontology_path']
    with open(structural_ontology_path, 'r') as f:
        structural_ontology_info = json.load(f)
        print(structural_ontology_info)
    return structural_ontology_info


# 暂时弃用
def get_cross_atlas(species_name, atlas_name, zslice):
    SQL = '''SELECT ID, * FROM Cross_species_atlas WHERE species = '{}' AND atlas = '{}' limit 1;'''.format(
        species_name, atlas_name)
    cross_species_atlas_dict = myDB.queryall(SQL)
    if cross_species_atlas_dict is None:
        return None
    print(cross_species_atlas_dict)

    SQL = '''SELECT id, * FROM Species WHERE name = '{}' limit 1;'''.format(species_name)
    species_dict = myDB.queryall(SQL)
    species_id = species_dict['ID']

    cross_species_atlas_info = {
        'id': cross_species_atlas_dict['ID'],
        'src': os.path.join(project_dir, cross_species_atlas_dict['src'], str(species_id) + '_' + str(zslice) + '.svg'),
        #'src': os.path.join(cross_species_atlas_dict['src'], str(species_id) + '_' + str(zslice) + '.svg'),
        'width': cross_species_atlas_dict['width'],
        'height': cross_species_atlas_dict['height']
    }
    print(cross_species_atlas_info)
    return cross_species_atlas_info


# 根据ontology id获取某张zslice的脑区svg，详情见api文档
def get_species_atlas(ontology_id, zslice):
    SQL = '''SELECT ID, * FROM Species_atlas WHERE ontology_id = '{}' limit 1;'''.format(ontology_id)
    species_atlas_dict = myDB.queryall(SQL)
    if species_atlas_dict is None or species_atlas_dict == {}:
        return None
    print(species_atlas_dict)

    # src = (os.path.join(project_dir, species_atlas_dict['src'], str(ontology_id) + '_' + str(zslice) + '.svg')).replace("\\","/")
    src = (os.path.join(species_atlas_dict['src'], str(ontology_id) + '_' + str(zslice) + '.svg')).replace("\\", "/")
    species_atlas_info = {
        'id': species_atlas_dict['ID'],
        'src': src,
        'width': species_atlas_dict['width'],
        'height': species_atlas_dict['height']
    }
    print(species_atlas_info)
    return species_atlas_info


# 根据ontology id和brain region id获取该脑区信息，详情见api文档
def get_brain_region_info(ontology_id, brain_region_id):
    SQL = '''SELECT ID, * FROM Species WHERE ontology_id = '{}' limit 1;'''.format(ontology_id)
    species_dict = myDB.queryall(SQL)
    if species_dict is None or species_dict == {}:
        return None
    print(species_dict)

    SQL = '''SELECT ID, * FROM Brain_region WHERE ontology_id = '{}' AND id = '{}' limit 1;'''.format(
        ontology_id, brain_region_id)
    brain_region_dict = myDB.queryall(SQL)
    if brain_region_dict is None or brain_region_dict == {}:
        return None
    print(brain_region_dict)

    SQL = '''SELECT id, * FROM Atlas WHERE id = '{}' limit 1;'''.format(ontology_id)
    atlas_dict = myDB.queryall(SQL)
    if atlas_dict is None or atlas_dict == {}:
        return None
    print(atlas_dict)

    adjacent_brain_regions = []
    if brain_region_dict['adjacent_brain_regions'] != '':
        adjacent_brain_regions_id = brain_region_dict['adjacent_brain_regions'].split(',')
        print('adjacent_brain_regions_id', adjacent_brain_regions_id)
        for adjacent_brain_region_id in adjacent_brain_regions_id:
            print(adjacent_brain_region_id)
            if adjacent_brain_regions_id == '':
                continue
            SQL = '''SELECT ID, * FROM Brain_region WHERE ontology_id = '{}' AND id = '{}' limit 1;'''.format(
                ontology_id, int(adjacent_brain_region_id))
            adjacent_brain_region_dict = myDB.queryall(SQL)
            if adjacent_brain_region_dict is None or adjacent_brain_region_dict == {}:
                return None
            adjacent_brain_regions.append({
                'id': adjacent_brain_region_dict['ID'],
                'name': adjacent_brain_region_dict['name'],
                'acronym': adjacent_brain_region_dict['acronym']
            })

    related_brain_regions = []
    if brain_region_dict['related_brain_regions'] != '':
        related_brain_regions_str_list = brain_region_dict['related_brain_regions'].split('#')
        for related_brain_regions_str in related_brain_regions_str_list:
            related_ontology_id = int(related_brain_regions_str.split(':')[0])
            SQL = '''SELECT id, * FROM Atlas WHERE id = '{}' limit 1;'''.format(related_ontology_id)
            related_atlas_dict = myDB.queryall(SQL)
            if related_atlas_dict is None or related_atlas_dict == {}:
                return None
            SQL = '''SELECT ID, * FROM Species WHERE ontology_id = '{}' limit 1;'''.format(related_ontology_id)
            related_species_dict = myDB.queryall(SQL)
            if related_species_dict is None or related_species_dict == {}:
                return None
            related_brain_region = {
                'atlas': related_atlas_dict['name'],
                'ontology_id': related_ontology_id,
                'species': related_species_dict['name'],
                'species_id': related_species_dict['ID'],
                'brain_regions': []
            }
            related_brain_regions_id = related_brain_regions_str.split(':')[1].split(',')
            for related_brain_region_id in related_brain_regions_id:
                SQL = '''SELECT ID, * FROM Brain_region WHERE ontology_id = '{}' AND id = '{}' limit 1;'''.format(
                    related_ontology_id, int(related_brain_region_id))
                related_brain_region_dict = myDB.queryall(SQL)
                if related_brain_region_dict is None or related_brain_region_dict == {}:
                    return None
                related_brain_region['brain_regions'].append({
                    'id': related_brain_region_dict['ID'],
                    'name': related_brain_region_dict['name'],
                    'acronym': related_brain_region_dict['acronym']
                })
            related_brain_regions.append(related_brain_region)

    zslices_str = brain_region_dict['zslices']
    zslices_list = []
    if zslices_str != '-1':
        zslices_list_tmp = zslices_str.split(',')
        zslices_list = [int(s) for s in zslices_list_tmp]

    brain_region_info = {
        'atlas': atlas_dict['name'],
        'species': species_dict['name'],
        'acronym': brain_region_dict['acronym'],
        'name': brain_region_dict['name'],
        'neurons_num': brain_region_dict['neurons_num'],
        'neurons_src': brain_region_dict['neurons_src'],
        'adjacent_brain_regions': adjacent_brain_regions,
        'related_brain_regions': related_brain_regions,
        'zslices': zslices_list
    }
    print(brain_region_info)
    return brain_region_info


if __name__ == '__main__':
    get_all_species()
    # get_species_info(57699)
    # get_image('57699', 'label', 2)
    # get_thumbnail_list("57698", "label")
    # get_structural_ontology(1)
    # get_cross_atlas('Developing Mouse', 'XX', 2)
    # get_species_atlas(1, 2)
    get_brain_region_info(1, 378)
    # get_brain_region_info(1,1113)

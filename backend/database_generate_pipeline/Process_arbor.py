import sqlite3
import pandas as pd
import json

base_brain_region_csv = ''

def classify_cortical_layers(json_data, cortical_layers):
    layer_data = {layer: [] for layer in cortical_layers}
    for item in json_data:
        if 315 in item['structure_id_path']:
            for layer in cortical_layers:
                if layer.replace("L", "") in item['acronym']:
                    layer_data[layer].append(item['id'])
                    break
    return layer_data


def find_brain_region_by_acronym_with_children_ids(acronym, json_data):
    for item in json_data:
        if item['acronym'] == acronym:
            children_ids = []
            for child in json_data:
                if item['id'] in child['structure_id_path']:
                    children_ids.append(child['id'])
            return {
                'id': item['id'],
                'acronym': acronym,
                'brain_region': item['name'],
                'children_ids': children_ids
            }
    return None


def get_child_list(celltype):
    # 读取CSV文件
    extracted_data = pd.read_csv("../config/id2celltype.csv")

    # 转换 'child_ids' 列从字符串到整数列表
    extracted_data['child_ids'] = extracted_data['child_ids'].apply(
        lambda x: [int(id_) for id_ in x.strip('[]').split(', ')] if x.strip('[]') else [])

    # 查找指定 celltype 的 child_ids
    try:
        child_ids = extracted_data.loc[extracted_data['acronym'] == celltype, 'child_ids'].iloc[0]
    except IndexError:
        return []  # 如果没有找到指定的 celltype, 返回空列表

    # 将 child_ids 中的每个 id 转换为相应的 acronym
    child_list = []
    for child_id in child_ids:
        acronym = extracted_data.loc[extracted_data['id'] == child_id, 'acronym'].iloc[0]
        child_list.append(acronym)

    return child_list


def prepare_data(data_path, extracted_data_path):
    # Load the ION data and the extracted data with children IDs
    ion_data = pd.read_csv(data_path, index_col=0)
    extracted_data = pd.read_csv(extracted_data_path)

    # Convert the children IDs column from string to list of integers
    extracted_data['children_ids'] = extracted_data['children_ids'].apply(
        lambda x: [int(id_) for id_ in x.split(', ')] if x else [])

    # Create mappings
    brain_region_to_children_ids = {row['id']: row['children_ids'] for _, row in extracted_data.iterrows() if
                                    pd.notnull(row['id'])}
    acronym_to_children_ids = {row['acronym']: row['children_ids'] for _, row in extracted_data.iterrows() if
                               pd.isnull(row['id'])}
    id_to_acronym = {row['id']: row['acronym'] for _, row in extracted_data.iterrows() if pd.notnull(row['id'])}

    return ion_data, brain_region_to_children_ids, acronym_to_children_ids, id_to_acronym


def calculate_projection_values(ion_data, brain_region_to_children_ids, acronym_to_children_ids, id_to_acronym):
    projection_values_df = pd.DataFrame()

    # Iterate through each SWC in the ION data
    for swc_id, swc_row in ion_data.iterrows():
        projection_values = {}
        # Calculate projection values for regions with id
        for brain_region_id, children_ids in brain_region_to_children_ids.items():
            # num_elements = len([brain_region_id] + children_ids)
            # if num_elements > 0:
            #     projection_value = sum(
            #         swc_row.get(str(id_), 0) for id_ in [brain_region_id] + children_ids) / num_elements
            # else:
            #     projection_value = 0
            projection_value = sum(swc_row.get(str(id_), 0) for id_ in children_ids)
            projection_values[id_to_acronym[brain_region_id]] = projection_value
        # Calculate projection values for regions without id (cortical layers)
        for acronym, children_ids in acronym_to_children_ids.items():
            # num_elements = len(children_ids)
            # if num_elements > 0:
            #     projection_value = sum(swc_row.get(str(id_), 0) for id_ in children_ids) / num_elements
            # else:
            #     projection_value = 0
            projection_value = sum(swc_row.get(str(id_), 0) for id_ in children_ids)
            projection_values[acronym] = projection_value
        projection_values_df[swc_id] = pd.Series(projection_values)

    # Transpose the DataFrame for easier column renaming and exporting
    transposed_projection_values_df = projection_values_df.T

    # Rename the columns to 'proj_axon_[acronym]_abs'
    transposed_projection_values_df.columns = ['proj_arbor_' + col + '_abs' for col in
                                               transposed_projection_values_df.columns]

    return transposed_projection_values_df


def calculate_projection_values_dar(ion_data, brain_region_to_children_ids, acronym_to_children_ids, id_to_acronym):
    projection_values_df = pd.DataFrame()
    # Iterate through each SWC in the ION data
    for swc_id, swc_row in ion_data.iterrows():
        projection_values = {}
        # Calculate projection values for regions with id
        for brain_region_id, children_ids in brain_region_to_children_ids.items():
            child_temp = []
            for _id in children_ids:
                if swc_row.get(str(_id)) != 0:
                    child_temp.append(_id)
            num_elements = len(child_temp)
            if num_elements > 0:
                projection_value = sum(
                    swc_row.get(str(id_), 0) for id_ in child_temp) / num_elements
            else:
                projection_value = 0
            # projection_value = sum(swc_row.get(str(id_), 0) for id_ in [brain_region_id] + children_ids)
            projection_values[id_to_acronym[brain_region_id]] = projection_value
        # Calculate projection values for regions without id (cortical layers)
        for acronym, children_ids in acronym_to_children_ids.items():
            child_temp = []
            for _id in children_ids:
                if swc_row.get(str(_id)) != 0:
                    child_temp.append(_id)
            num_elements = len(child_temp)
            if num_elements > 0:
                projection_value = sum(swc_row.get(str(id_), 0) for id_ in child_temp) / num_elements
            else:
                projection_value = 0
            # projection_value = sum(swc_row.get(str(id_), 0) for id_ in children_ids)
            projection_values[acronym] = projection_value
        projection_values_df[swc_id] = pd.Series(projection_values)

    # Transpose the DataFrame for easier column renaming and exporting
    transposed_projection_values_df = projection_values_df.T

    # Rename the columns to 'proj_axon_[acronym]_abs'
    transposed_projection_values_df.columns = ['proj_arbor_' + col + '_dar' for col in
                                               transposed_projection_values_df.columns]

    return transposed_projection_values_df


# STEP 1
def extract_brain_region():
    # 数据库文件路径和表名
    db_file = '../database/test_0410.db'  # 替换为您的数据库文件路径
    table_name = 'Projection_Dendrite'  # 指定的表名

    # 连接到 SQLite 数据库
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 获取指定表的列名
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    columns = [description[1] for description in cursor.fetchall()]

    # 处理每个列名字符串，只保留 split("_")[2]
    processed_columns = []
    for col in columns:
        parts = col.split("_")
        if len(parts) >= 3:
            processed_columns.append(parts[2])
        else:
            processed_columns.append(col)  # 如果列名不包含足够的下划线，保留原始列名

    # 将处理后的列名转换为 DataFrame
    df_processed_columns = pd.DataFrame(processed_columns, columns=['Processed Column Name'])

    # 将 DataFrame 写入新的 CSV 文件
    processed_csv_file = r'D:\NeuroXiv\ALL_DATA_TABLES\Process_Proj_Base_table\base_brain_region.csv'
    df_processed_columns.to_csv(processed_csv_file, index=False)
    # 关闭数据库连接
    conn.close()
    return processed_csv_file


# STEP 2
# 提取出所有脑区，以及所有脑区包含的子脑区和皮层脑区
def extract_complete_brain_region():
    # Load the JSON data
    with open(r'D:\NeuroXiv\tree.json', 'r', encoding='utf-8') as file:
        tree_data = json.load(file)

    # Display the type and length of tree_data
    print("Type of tree_data:", type(tree_data))
    print("Number of items in tree_data:", len(tree_data))

    csv_file_path = r'D:\NeuroXiv\ALL_DATA_TABLES\Process_Proj_Base_table\base_brain_region.csv'
    csv_data = pd.read_csv(csv_file_path)
    brain_regions_csv = csv_data['Processed Column Name'].unique()
    # Extract the information for each brain region acronym in the CSV file
    extracted_data = [
        find_brain_region_by_acronym_with_children_ids(acronym, tree_data)
        for acronym in brain_regions_csv
    ]
    # Filter out None values (regions not found in the JSON data)
    extracted_data = [data for data in extracted_data if data is not None]
    # Function to classify each brain region as a child of a specific cortical layer
    cortical_layers = ['L1', 'L2/3', 'L4', 'L5', 'L6a', 'L6b']
    cortical_layer_data = classify_cortical_layers(tree_data, cortical_layers)

    # Add the cortical layers and their children to the extracted data
    for layer, children_ids in cortical_layer_data.items():
        layer_data = {
            'id': None,
            'acronym': layer,
            'brain_region': layer + ' cortical layer',
            'children_ids': children_ids
        }
        extracted_data.append(layer_data)

    # Convert the extracted data to a DataFrame for CSV export
    combined_df = pd.DataFrame(extracted_data)
    combined_df['children_ids'] = combined_df['children_ids'].apply(lambda x: ', '.join(map(str, x)))
    # Export to CSV
    output_csv_path_with_children_ids = r'D:\NeuroXiv\ALL_DATA_TABLES\Process_Proj_Base_table\complete_brain_region.csv'
    combined_df.to_csv(output_csv_path_with_children_ids, index=False)


# STEP 3
def calAbsData():
    # Paths to the data files (replace with actual paths)
    data_path = r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\abor_tables\arbor_absolute.csv'
    extracted_data_path = r'D:\NeuroXiv\ALL_DATA_TABLES\Process_Proj_Base_table\complete_brain_region.csv'

    # Prepare data and mappings
    data, brain_region_to_children_ids, acronym_to_children_ids, id_to_acronym = prepare_data(data_path,
                                                                                              extracted_data_path)

    # Calculate projection values
    transposed_projection_values_df = calculate_projection_values(data, brain_region_to_children_ids,
                                                                  acronym_to_children_ids, id_to_acronym)

    # Output the adjusted DataFrame to a CSV file (replace with actual output path)
    output_csv_path = r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\Proj_Arbor_CCFv3_abs.csv'
    transposed_projection_values_df.to_csv(output_csv_path)


def calDarData():
    # Paths to the data files (replace with actual paths)
    data_path = r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\abor_tables\arbor_dar.csv'
    extracted_data_path = r'D:\NeuroXiv\ALL_DATA_TABLES\Process_Proj_Base_table\complete_brain_region.csv'

    # Prepare data and mappings
    data, brain_region_to_children_ids, acronym_to_children_ids, id_to_acronym = prepare_data(data_path,
                                                                                              extracted_data_path)

    # Calculate projection values
    transposed_projection_values_df = calculate_projection_values_dar(data, brain_region_to_children_ids,
                                                                      acronym_to_children_ids, id_to_acronym)

    # Output the adjusted DataFrame to a CSV file (replace with actual output path)
    output_csv_path = r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\Proj_Arbor_CCFv3_dar_0511.csv'
    transposed_projection_values_df.to_csv(output_csv_path)


# STEP 4
def calRelaData():
    adjusted_projection_values_df = pd.read_csv(
        r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\Proj_Arbor_CCFv3_abs.csv',
        index_col=0)

    # Calculate the sum of projection values for each SWC
    sum_projection_values = adjusted_projection_values_df.sum(axis=1)

    # Calculate the relative projection values for each brain region
    relative_projection_values_df = adjusted_projection_values_df.div(sum_projection_values, axis=0)

    # Rename the columns to 'proj_den_[acronym]_rela'
    relative_projection_values_df.columns = [col.replace('_abs', '_rela') for col in
                                             relative_projection_values_df.columns]

    # Combine the absolute and relative projection values dataframes
    combined_df = pd.concat([adjusted_projection_values_df, relative_projection_values_df], axis=1)

    # Reordering columns so that each relative value column is followed by its absolute value column
    columns_order = [val for pair in zip(relative_projection_values_df.columns, adjusted_projection_values_df.columns)
                     for
                     val in pair]
    reordered_combined_df = combined_df[columns_order]

    # Save the reordered combined DataFrame to a new CSV file
    reordered_combined_csv_path = r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\Proj_Arbor_CCFv3_Middle.csv'
    reordered_combined_df.to_csv(reordered_combined_csv_path)


def extract_key(col_name):
    """从列名中提取关键词作为匹配依据"""
    if 'proj_arbor_' in col_name:
        parts = col_name.split('_')
        if len(parts) > 2:
            return parts[2]  # 返回匹配关键词
    return None


# # step 5
def calFinalData():
    # 创建列名与关键词映射
    middle_df = pd.read_csv(r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\Proj_Arbor_CCFv3_Middle.csv',
                            index_col=0)
    dar_df = pd.read_csv(r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\Proj_Arbor_CCFv3_dar_0511.csv', index_col=0)
    middle_keys = {col: extract_key(col) for col in middle_df.columns}
    dar_keys = {col: extract_key(col) for col in dar_df.columns}

    # 用于跟踪每个关键词最后一个匹配列的位置
    last_insert_positions = {}

    # 遍历 dar_df 的列，找到匹配的列，并按顺序插入到 middle_df 中
    for dar_col, dar_key in dar_keys.items():
        if dar_key:  # 确保 dar_key 不是 None
            insert_pos = None
            # 寻找匹配的最后一个middle列的位置
            for middle_col, middle_key in middle_keys.items():
                if dar_key == middle_key:
                    # 更新插入位置为当前匹配列的下一位置
                    insert_pos = middle_df.columns.get_loc(middle_col) + 1

            # 如果找到了匹配列
            if insert_pos is not None:
                # 如果此关键词之前已插入过列，则将新列插入到最后一次插入的列之后
                if dar_key in last_insert_positions:
                    insert_pos = max(insert_pos, last_insert_positions[dar_key] + 1)

                # 插入列
                middle_df.insert(loc=insert_pos, column=dar_col, value=dar_df[dar_col])

                # 更新这个关键词的最后插入位置
                last_insert_positions[dar_key] = insert_pos
    # 显示更新后的 middle_df 的前几行，确认插入成功
    print(middle_df.head())
    middle_df.to_csv(r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\Proj_Arbor_Final_0511.csv')


if __name__ == '__main__':
    # extract_brain_region()
    # extract_complete_brain_region()
    calAbsData()
    calDarData()
    calRelaData()
    calFinalData()

import os
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


def calculate_projection_axon_values(ion_data, brain_region_to_children_ids, acronym_to_children_ids, id_to_acronym):
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
            projection_value = sum(swc_row.get(str(id_), 0) for id_ in [brain_region_id] + children_ids)
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
    transposed_projection_values_df.columns = ['proj_axon_' + col + '_abs' for col in
                                               transposed_projection_values_df.columns]

    return transposed_projection_values_df


def calculate_projection_dendrite_values(ion_data, brain_region_to_children_ids, acronym_to_children_ids,
                                         id_to_acronym):
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
            projection_value = sum(swc_row.get(str(id_), 0) for id_ in [brain_region_id] + children_ids)
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
    transposed_projection_values_df.columns = ['proj_den_' + col + '_abs' for col in
                                               transposed_projection_values_df.columns]

    return transposed_projection_values_df


def calculate_projection_local_values(ion_data, brain_region_to_children_ids, acronym_to_children_ids,
                                      id_to_acronym):
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
            projection_value = sum(swc_row.get(str(id_), 0) for id_ in [brain_region_id] + children_ids)
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
    transposed_projection_values_df.columns = ['proj_den_' + col + '_abs' for col in
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
def calAxonAbsData(data_path):
    # Paths to the data files (replace with actual paths)
    # data_path = r'D:\NeuroXiv\ALL_DATA_TABLES\NeuroXiv_tables_V20240408\arbor_absolute.csv'
    save_folder = os.path.dirname(data_path)
    data_path = data_path
    extracted_data_path = r'D:\NeuroXiv\ALL_DATA_TABLES\Process_Proj_Base_table\complete_brain_region.csv'

    # Prepare data and mappings
    data, brain_region_to_children_ids, acronym_to_children_ids, id_to_acronym = prepare_data(data_path,
                                                                                              extracted_data_path)

    # Calculate projection values
    transposed_projection_values_df = calculate_projection_axon_values(data, brain_region_to_children_ids,
                                                                       acronym_to_children_ids, id_to_acronym)

    # Output the adjusted DataFrame to a CSV file (replace with actual output path)
    output_csv_path = os.path.join(save_folder, 'Proj_Axon_abs.csv')
    transposed_projection_values_df.to_csv(output_csv_path)
    return output_csv_path


def calDenAbsData(data_path):
    save_folder = os.path.dirname(data_path)
    data_path = data_path
    extracted_data_path = r'D:\NeuroXiv\ALL_DATA_TABLES\Process_Proj_Base_table\complete_brain_region.csv'

    # Prepare data and mappings
    data, brain_region_to_children_ids, acronym_to_children_ids, id_to_acronym = prepare_data(data_path,
                                                                                              extracted_data_path)

    # Calculate projection values
    transposed_projection_values_df = calculate_projection_dendrite_values(data, brain_region_to_children_ids,
                                                                           acronym_to_children_ids, id_to_acronym)

    # Output the adjusted DataFrame to a CSV file (replace with actual output path)
    output_csv_path = os.path.join(save_folder, 'Proj_Den_abs.csv')
    transposed_projection_values_df.to_csv(output_csv_path)
    return output_csv_path


def calLocalAbsData(data_path):
    save_folder = os.path.dirname(data_path)
    data_path = data_path
    extracted_data_path = r'D:\NeuroXiv\ALL_DATA_TABLES\Process_Proj_Base_table\complete_brain_region.csv'

    # Prepare data and mappings
    data, brain_region_to_children_ids, acronym_to_children_ids, id_to_acronym = prepare_data(data_path,
                                                                                              extracted_data_path)

    # Calculate projection values
    transposed_projection_values_df = calculate_projection_dendrite_values(data, brain_region_to_children_ids,
                                                                           acronym_to_children_ids, id_to_acronym)

    # Output the adjusted DataFrame to a CSV file (replace with actual output path)
    output_csv_path = os.path.join(save_folder, 'Proj_local_abs.csv')
    transposed_projection_values_df.to_csv(output_csv_path)
    return output_csv_path


# STEP 4
def calAxonRelaData(data_path):
    save_folder = os.path.dirname(data_path)
    adjusted_projection_values_df = pd.read_csv(data_path, index_col=0)

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
    reordered_combined_csv_path = os.path.join(save_folder, 'Proj_Axon_Final.csv')
    reordered_combined_df.to_csv(reordered_combined_csv_path)


def calDenRelaData(data_path):
    save_folder = os.path.dirname(data_path)
    adjusted_projection_values_df = pd.read_csv(data_path, index_col=0)

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
    reordered_combined_csv_path = os.path.join(save_folder, 'Proj_Den_Final.csv')
    reordered_combined_df.to_csv(reordered_combined_csv_path)


def callocalRelaData(data_path):
    save_folder = os.path.dirname(data_path)
    adjusted_projection_values_df = pd.read_csv(data_path, index_col=0)

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
    reordered_combined_csv_path = os.path.join(save_folder, 'Proj_local_Final.csv')
    reordered_combined_df.to_csv(reordered_combined_csv_path)


if __name__ == '__main__':
    axon_path = r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\local_proj.csv'
    den_path = r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\axon_den_features_v0424\denfull_proj.csv'
    local_path = r'D:\NeuroXiv\ALL_DATA_TABLES\tables_v20240419\local_proj.csv'
    # axon_abs = calAxonAbsData(axon_path)
    # calAxonRelaData(axon_abs)
    # den_abs = calDenAbsData(den_path)
    # calDenRelaData(den_abs)
    local_abs = calLocalAbsData(local_path)
    callocalRelaData(local_abs)

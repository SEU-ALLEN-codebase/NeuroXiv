import pandas as pd


def process_projection_matrix(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path, index_col=0)

    # 获取神经元ID列表
    neuron_ids = df.columns.tolist()

    # 创建一个空的结果DataFrame
    result = pd.DataFrame(columns=['Neuron', 'Similar Neurons'])

    # 遍历每一行
    for neuron in df.index:
        # 获取当前神经元的相似度系列
        similarity_series = df.loc[neuron]
        print(len(similarity_series))

        # 将相似度与ID配对并筛选小于等于0.3的值
        similarity_pairs = [(neuron_id, similarity) for neuron_id, similarity in zip(neuron_ids, similarity_series) if
                            similarity <= 0.1]
        print(len(similarity_pairs))
        # 按相似度从小到大排序
        similarity_pairs = sorted(similarity_pairs, key=lambda x: x[1])

        # 获取排序后的ID列表
        sorted_similar_neurons = [pair[0] for pair in similarity_pairs[:500]]

        # 添加到结果DataFrame
        result = result.append({'Neuron': neuron, 'Similar Neurons': ', '.join(sorted_similar_neurons)},
                               ignore_index=True)

    return result


# 调用函数并保存结果
# file_path = r'D:\NeuroXiv\ALL_DATA_TABLES\axon_pdistance_nor_maxdist_1522.2.csv'  # 修改为你的CSV文件路径
file_path = r'D:\NeuroXiv\ALL_DATA_TABLES\axonfea_similarity.csv\axonfea_similarity.csv'  # 修改为你的CSV文件路径
processed_matrix = process_projection_matrix(file_path)
processed_matrix.to_csv(r'D:\NeuroXiv\ALL_DATA_TABLES\morpho_similar.csv', index=False)

print(processed_matrix)

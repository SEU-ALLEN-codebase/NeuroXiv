from nltk.tokenize import sent_tokenize, word_tokenize
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import re
import torch

# 确保你已经下载了必要的NLTK资源
# nltk.download('punkt')

# 检查是否有可用的 GPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 加载用于计算语义相似度的模型
model = SentenceTransformer('paraphrase-MiniLM-L6-v2', device=device)

# 加载用于推理的模型
inference_model = SentenceTransformer('stsb-roberta-large', device=device)


def extract_numbers(text):
    return re.findall(r'\b\d+\.?\d*\b', text)


def check_number_accuracy(reference_numbers, hypothesis_numbers, reference_text, hypothesis_text):
    if len(hypothesis_numbers) == 0:
        return 1  # 如果hypothesis_numbers为空，返回1表示数字准确性为100%

    correct_numbers = set(reference_numbers).intersection(set(hypothesis_numbers))
    incorrect_numbers = set(hypothesis_numbers) - set(reference_numbers)

    inferred_correct_numbers = set()
    for num in incorrect_numbers:
        for hyp_sentence in sent_tokenize(hypothesis_text):
            if num in hyp_sentence:
                for ref_sentence in sent_tokenize(reference_text):
                    if num in ref_sentence:
                        inferred_correct_numbers.add(num)
                        break
                    inference_similarity = calculate_inference(ref_sentence, hyp_sentence)
                    logical_similarity = check_logical_expression(ref_sentence, hyp_sentence)
                    if inference_similarity > 0.75 or logical_similarity > 0.75:
                        inferred_correct_numbers.add(num)
                        break

    total_correct_numbers = correct_numbers.union(inferred_correct_numbers)
    return len(total_correct_numbers) / len(hypothesis_numbers)


def check_logical_expression(reference_sentence, hypothesis_sentence):
    reference_embedding = model.encode(reference_sentence, convert_to_tensor=True)
    hypothesis_embedding = model.encode(hypothesis_sentence, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(reference_embedding, hypothesis_embedding).item()
    return similarity


def calculate_inference(reference_sentence, hypothesis_sentence):
    ref_embedding = inference_model.encode(reference_sentence, convert_to_tensor=True)
    hyp_embedding = inference_model.encode(hypothesis_sentence, convert_to_tensor=True)
    inference_similarity = util.pytorch_cos_sim(ref_embedding, hyp_embedding).item()
    return inference_similarity


def calculate_data_accuracy(reference, hypothesis):
    reference_sentences = sent_tokenize(reference)
    hypothesis_sentences = sent_tokenize(hypothesis)

    reference_numbers = extract_numbers(reference)
    hypothesis_numbers = extract_numbers(hypothesis)

    # 计算数字准确性
    number_accuracy = check_number_accuracy(reference_numbers, hypothesis_numbers, reference, hypothesis)

    correct_logical_count = 0
    total_logical_count = 0
    for hyp_sentence in hypothesis_sentences:
        hyp_numbers = extract_numbers(hyp_sentence)
        if not hyp_numbers:
            continue
        for ref_sentence in reference_sentences:
            ref_numbers = extract_numbers(ref_sentence)
            if set(hyp_numbers).issubset(set(ref_numbers)) or all(num in reference for num in hyp_numbers):
                logical_similarity = check_logical_expression(ref_sentence, hyp_sentence)
                inference_similarity = calculate_inference(ref_sentence, hyp_sentence)
                total_logical_count += 1
                if logical_similarity > 0.75 or inference_similarity > 0.75:  # 设置语义和推理相似度阈值
                    correct_logical_count += 1
                    break  # 只要找到一个匹配的句子，就可以跳出循环

    logical_accuracy = correct_logical_count / total_logical_count if total_logical_count != 0 else 1

    # 打印调试信息
    # print(f"Number Accuracy: {number_accuracy}")
    # print(f"Logical Accuracy: {logical_accuracy}")
    # print(f"Correct Logical Count: {correct_logical_count}")
    # print(f"Total Logical Count: {total_logical_count}")

    return number_accuracy, logical_accuracy


def map_to_score(ratio):
    if ratio >= 0.9:
        return 5
    elif ratio >= 0.7:
        return 4
    elif ratio >= 0.5:
        return 3
    elif ratio >= 0.3:
        return 2
    else:
        return 1


def calculate_semantic_similarity(reference, hypothesis):
    reference_embedding = model.encode(reference, convert_to_tensor=True)
    hypothesis_embedding = model.encode(hypothesis, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(reference_embedding, hypothesis_embedding).item()
    return similarity


def calculate_conciseness(reference, hypothesis):
    ref_length = len(reference.split())
    hyp_length = len(hypothesis.split())
    conciseness = hyp_length / ref_length if ref_length != 0 else 1
    return conciseness


def calculate_originality(hypothesis):
    words = word_tokenize(hypothesis)
    unique_words = set(words)
    originality = len(unique_words) / len(words) if len(words) != 0 else 1
    return originality


def calculate_information_density(reference, hypothesis):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([reference, hypothesis])
    feature_names = vectorizer.get_feature_names_out()
    dense = tfidf_matrix.todense()
    denselist = dense.tolist()

    ref_tfidf = dict(zip(feature_names, denselist[0]))
    hyp_tfidf = dict(zip(feature_names, denselist[1]))

    key_info_ref = {word: score for word, score in ref_tfidf.items() if score > 0.1}  # 选择TF-IDF值较高的关键词作为关键信息
    key_info_hyp = {word: score for word, score in hyp_tfidf.items() if word in key_info_ref}

    info_density = len(key_info_hyp) / len(hypothesis.split()) if len(hypothesis.split()) != 0 else 1
    return info_density


def map_density_to_score(density):
    if density >= 0.95:
        return 5
    elif density >= 0.75:
        return 4
    elif density >= 0.55:
        return 3
    elif density >= 0.35:
        return 2
    else:
        return 1


def map_density_to_score_Conciseness(density):
    if density >= 0.95:
        return 1
    elif density >= 0.75:
        return 2
    elif density >= 0.55:
        return 3
    elif density >= 0.35:
        return 4
    else:
        return 5


def map_density_to_score_InfoDensity(density):
    if density >= 0.5:
        return 5
    elif density >= 0.4:
        return 4
    elif density >= 0.3:
        return 3
    elif density >= 0.2:
        return 2
    else:
        return 1


def summarize_text(summary, origin_input):
    evaluation_summary = ""

    # 计算数据准确性
    number_accuracy, logical_accuracy = calculate_data_accuracy(origin_input, summary)
    data_accuracy_ratio = number_accuracy * 0.9 + logical_accuracy * 0.1
    data_accuracy_score = map_to_score(data_accuracy_ratio)

    # 计算语义相似度并映射到1-5分
    semantic_similarity = calculate_semantic_similarity(origin_input, summary)
    semantic_similarity_mapped = map_to_score(semantic_similarity)

    # 计算简洁性并映射到1-5分
    conciseness = calculate_conciseness(origin_input, summary)
    conciseness_mapped = map_density_to_score_Conciseness(conciseness)

    # 计算原创性并映射到1-5分
    originality = calculate_originality(summary)
    originality_mapped = map_to_score(originality)

    # 计算信息密度并映射到1-5分
    information_density = calculate_information_density(origin_input, summary)
    information_density_mapped = map_density_to_score_InfoDensity(information_density)

    # 综合评分，使用权重平衡各指标
    weights = {
        'Data Accuracy': 0.4,
        'Semantic Similarity': 0.1,
        'Conciseness': 0.2,
        'Originality': 0.1,
        'Information Density': 0.2
    }
    overall_score = (weights['Data Accuracy'] * data_accuracy_score +
                     weights['Semantic Similarity'] * semantic_similarity_mapped +
                     weights['Conciseness'] * conciseness_mapped +
                     weights['Originality'] * originality_mapped +
                     weights['Information Density'] * information_density_mapped)

    # 生成评估报告
    evaluation_summary += "Evaluation Summary:\n\n"
    evaluation_summary += f"Data Accuracy: {data_accuracy_ratio:.4f} (Score: {data_accuracy_score}, Number Accuracy: {number_accuracy:.4f}, Logical Accuracy: {logical_accuracy:.4f})\n"
    evaluation_summary += f"Semantic Similarity: {semantic_similarity:.4f} (Score: {semantic_similarity_mapped})\n"
    evaluation_summary += f"Conciseness: {conciseness:.4f} (Score: {conciseness_mapped})\n"
    evaluation_summary += f"Originality: {originality:.4f} (Score: {originality_mapped})\n"
    evaluation_summary += f"Information Density: {information_density:.4f} (Score: {information_density_mapped})\n"
    evaluation_summary += f"Overall Score: {overall_score:.4f}\n"

    scores = {
        'Data Accuracy': round(data_accuracy_ratio, 4),
        'Data Accuracy Score': data_accuracy_score,
        'Number Accuracy': round(number_accuracy, 4),
        'Logical Accuracy': round(logical_accuracy, 4),
        'Semantic Similarity': round(semantic_similarity, 4),
        'Semantic Similarity Score': semantic_similarity_mapped,
        'Conciseness': round(conciseness, 4),
        'Conciseness Score': conciseness_mapped,
        'Originality': round(originality, 4),
        'Originality Score': originality_mapped,
        'Information Density': round(information_density, 4),
        'Information Density Score': information_density_mapped,
        'Overall': round(overall_score, 4)
    }

    return evaluation_summary, scores


# 示例用法
origin_input = """The dendritic arbor data (CA1 neurons) obtained from the ION source reveals the following arborized patterns:
(The format is as follows: brain region name is listed in descending order of length, along with the proportion of arborized length within that brain region.)
- CA1: 6119.3 μm (77.6%).
The dendritic arbor data (DG neurons) obtained from the ION source reveals the following arborized patterns:
(The format is as follows: brain region name is listed in descending order of length, along with the proportion of arborized length within that brain region.)
- DG: 2415.1 μm (91.0%).

The axonal arbor data (CA1 neurons) obtained from the ION source reveals the following arborized patterns:
(The format is as follows: brain region name is listed in descending order of length, along with the proportion of arborized length within that brain region.)
- CA1: 18260.3 μm (23.7%).
- LSr: 6139.4 μm (6.7%).
- ACB: 4626.1 μm (5.1%).
- SUB: 2992.0 μm (4.7%).
- ProS: 2805.2 μm (4.5%).
- AON: 3585.6 μm (3.8%).
- ENTl: 2816.3 μm (3.1%).
- PA: 1319.3 μm (2.4%).
- CA3: 2270.6 μm (2.1%).
- DG: 1218.8 μm (1.8%).
- COAp: 1029.4 μm (1.3%).
The axonal arbor data (DG neurons) obtained from the ION source reveals the following arborized patterns:
(The format is as follows: brain region name is listed in descending order of length, along with the proportion of arborized length within that brain region.)
- CA3: 2061.9 μm (45.3%).
- DG: 2244.3 μm (42.4%)."""
summary = "The dataset consists of 150 neurons from three sources: ION (127 neurons), SEU-ALLEN (12 neurons), " \
          "and MouseLight (11 neurons). These neurons include 150 axons, 61 basal dendrites, 4 apical dendrites, " \
          "and no local dendrites. Spatially, 42 neurons are in the left hemisphere and 108 in the right. The neurons " \
          "are distributed across 30 brain regions, with the highest counts in CA1 (33 neurons), DG (24 neurons), " \
          "and MOs (14 neurons). Furthermore, 55 neurons are located in specific cortical layers, predominantly in L5 " \
          "(29 neurons), L2/3 (16 neurons), L6a (8 neurons), and minimally in L1 and L4 (1 neuron each). "

evaluation_summary, scores = summarize_text(summary, origin_input)
print(evaluation_summary)
print(scores)

import os
import re
import csv
import numpy as np
from collections import Counter
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
from nltk.tokenize import word_tokenize

# 加载预训练的句子嵌入模型
model = SentenceTransformer('all-MiniLM-L6-v2')


def count_tokens(text):
    if not isinstance(text, str):
        print(text)
        raise TypeError(f"Expected string or bytes-like object, got {type(text).__name__}")
    tokens = word_tokenize(text)
    return len(tokens)


def calculate_entropy(text):
    if not text:
        return 0
    words = text.split()
    word_freq = Counter(words)
    total_words = len(words)
    entropy = -sum((freq / total_words) * np.log2(freq / total_words) for freq in word_freq.values())
    return entropy


def calculate_semantic_entropy(text, num_clusters=5):
    if not text:
        return 0
    sentences = text.split('.')
    embeddings = model.encode(sentences)
    num_clusters = min(num_clusters, len(sentences))  # Ensure num_clusters is not greater than the number of sentences
    if num_clusters < 2:
        return 0  # Semantic entropy is zero if there is only one sentence or no sentence
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(embeddings)
    labels = kmeans.labels_
    label_freq = Counter(labels)
    total_labels = len(labels)
    entropy = -sum((freq / total_labels) * np.log2(freq / total_labels) for freq in label_freq.values())
    return entropy


def extract_summaries_from_log(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Define regex pattern for extracting blocks
    blocks_pattern = re.compile(r'(\[ORIGINAL TEXT\].*?)(?=\[ORIGINAL TEXT\]|\Z)', re.DOTALL)

    # Extract all blocks
    blocks = re.findall(blocks_pattern, content)

    all_data = []

    info_types = ['basic_info', 'morpho_info', 'proj_info']

    for i, block in enumerate(blocks):
        # Determine the info type based on the block index
        info_type = info_types[i % len(info_types)]

        # Extract original text
        original_text_match = re.search(r'\[ORIGINAL TEXT\]\n(.*?)(?=\[MODEL: Qwen\])', block, re.DOTALL)
        original_text = original_text_match.group(1).strip() if original_text_match else None

        # Initialize summaries dictionary
        summaries = {
            'Qwen': {'basic_info': '', 'morpho_info': '', 'proj_info': ''},
            'Mistral': {'basic_info': '', 'morpho_info': '', 'proj_info': ''},
            'Zhipu': {'basic_info': '', 'morpho_info': '', 'proj_info': ''},
            'GPT4o': {'basic_info': '', 'morpho_info': '', 'proj_info': ''},
            'MoE': {'basic_info': '', 'morpho_info': '', 'proj_info': ''}
        }

        # Extract and assign summaries for each model
        models = ['Qwen', 'Mistral', 'Zhipu', 'GPT4o', 'MoE']
        for model in models:
            model_pattern = re.compile(r'\[MODEL: {}\]\n(.*?)(?=\[MODEL: |\[ORIGINAL TEXT\]|\Z)'.format(model),
                                       re.DOTALL)
            model_summary_match = model_pattern.search(block)
            if model_summary_match:
                summaries_content = model_summary_match.group(1).strip()
                summaries_content = re.sub(r'\n\s*\n', '\n', summaries_content)  # Remove empty lines
                summaries[model][info_type] = summaries_content

        all_data.append((original_text, summaries, info_type))

    return all_data


def process_files_in_directory(directory):
    results = []

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            all_data = extract_summaries_from_log(file_path)
            print(filename)
            for i, (original_text, summaries, info_type) in enumerate(all_data):
                # Calculate entropy and semantic entropy for original text
                original_text_entropy = calculate_entropy(original_text)
                original_text_semantic_entropy = calculate_semantic_entropy(original_text)
                raw_token_count = count_tokens(original_text)

                for model, summary_types in summaries.items():
                    summary = summary_types[info_type]
                    entropy = calculate_entropy(summary)
                    semantic_entropy = calculate_semantic_entropy(summary)

                    results.append([
                        filename, i + 1, model, info_type,
                        entropy, semantic_entropy,
                        original_text_entropy, original_text_semantic_entropy,
                        raw_token_count
                    ])

    return results


# Specify the directory containing the .txt files
directory = r'D:\NeuroXiv\api\MoE\log_0726_batch\test4'
results = process_files_in_directory(directory)

# Write results to CSV
csv_file_path = os.path.join(directory, 'summary_entropies_test4.csv')
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([
        'Filename', 'Block Number', 'Model', 'Info Type',
        'Entropy', 'Semantic Entropy',
        'Original Text Entropy', 'Original Text Semantic Entropy',
        'raw token count'
    ])
    writer.writerows(results)

print(f"Results saved to {csv_file_path}")

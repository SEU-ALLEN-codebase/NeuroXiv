from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import re
import numpy as np

# 检查是否有可用的 GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 加载NLI模型和分词器，并将模型移动到 GPU 上
model_name = "roberta-large-mnli"
nli_model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)
nli_tokenizer = AutoTokenizer.from_pretrained(model_name)

# 加载用于计算余弦相似度的句子嵌入模型
embed_model = SentenceTransformer(r'D:\NeuroXiv\api\all-mpnet-base-v2', device=device)

# 定义原始文本和总结
origin_text = """The dendritic arbor data (DG neurons) obtained from the ION source reveals the following arborized patterns:
(The format is as follows: brain region name is listed in descending order of length, along with the proportion of arborized length within that brain region.)
- DG: 2309.8 μm (82.7%).
The dendritic arbor data (CA1 neurons) obtained from the ION source reveals the following arborized patterns:
(The format is as follows: brain region name is listed in descending order of length, along with the proportion of arborized length within that brain region.)
- CA1: 5761.0 μm (79.1%).

The axonal arbor data (DG neurons) obtained from the ION source reveals the following arborized patterns:
(The format is as follows: brain region name is listed in descending order of length, along with the proportion of arborized length within that brain region.)
- CA3: 1865.5 μm (44.9%).
- DG: 1920.8 μm (42.8%).
The axonal arbor data (CA1 neurons) obtained from the ION source reveals the following arborized patterns:
(The format is as follows: brain region name is listed in descending order of length, along with the proportion of arborized length within that brain region.)
- CA1: 15030.2 μm (25.4%).
- LSr: 4807.4 μm (6.2%).
- ENTl: 4496.2 μm (6.1%).
- ENTm: 3453.6 μm (4.6%).
- ProS: 2465.4 μm (4.3%).
- SUB: 1939.8 μm (3.9%).
- CA3: 4465.2 μm (3.6%).
- ACB: 2686.8 μm (2.5%).
- SF: 1155.3 μm (1.7%).
- AM: 1397.4 μm (1.6%).
- PA: 1257.3 μm (1.3%).
- AON: 1450.8 μm (1.0%).
- BMA: 1026.6 μm (1.0%).
- COAp: 1081.0 μm (0.9%).
- TR: 1162.2 μm (0.8%).
"""

direct_summary = """The dendritic arbor data for DG neurons demonstrates a substantial arborization within the DG 
region, with a length of 2309.8 μm, accounting for 82.7% of the total arborized length. Comparatively, CA1 neurons 
show a significant dendritic reach within the CA1 region, totaling 5761.0 μm and representing 79.1% of the total 
dendritic length. In terms of axonal projections, DG neurons exhibit considerable connectivity to both CA3 and DG 
regions, with lengths of 1865.5 μm (44.9%) and 1920.8 μm (42.8%) respectively. On the other hand, CA1 neurons project 
extensively across multiple regions, with the highest axonal length in CA1 at 15030.2 μm (25.4%), followed by notable 
projections to LSr (4807.4 μm, 6.2%), ENTl (4496.2 μm, 6.1%), and several other regions, indicating a broad 
functional network. """

conbine_summary = """DG neurons display strong intraregional dendritic connectivity within the DG region, 
with a length of 2309.8 μm (82.7%), while CA1 neurons show extensive dendritic arborization within the CA1 area, 
measuring 5761.0 μm (79.1%). Axonal projections from DG neurons are evenly distributed between CA3 and DG regions, 
with lengths of 1865.5 μm (44.9%) and 1920.8 μm (42.8%) respectively. In contrast, CA1 neurons exhibit a broader 
axonal projection pattern, predominantly targeting the CA1 region (15030.2 μm, 25.4%) and distributing significantly 
to other brain regions like LSr, ENTl, and ENTm, indicating their role in widespread signal transmission. """

summary = conbine_summary
# 将总结分割为句子
summary_sentences = [sentence.strip() for sentence in summary.split('. ') if sentence]



# 用于推理判断的模板
def get_entailment_scores(premises, hypotheses):
    inputs = nli_tokenizer.batch_encode_plus(list(zip(premises, hypotheses)), return_tensors='pt', truncation=True,
                                             padding=True).to(device)
    with torch.cuda.amp.autocast():
        outputs = nli_model(**inputs)
    logits = outputs.logits
    entailment_scores = torch.softmax(logits, dim=1)[:, 2].detach().cpu().numpy()  # 标签为 'entailment' 的得分
    return entailment_scores


# 计算每个总结句子的推理得分
premises = [origin_text] * len(summary_sentences)
entailment_scores = get_entailment_scores(premises, summary_sentences)

# 计算余弦相似度得分
origin_embedding = embed_model.encode(origin_text, convert_to_tensor=True)
summary_embeddings = embed_model.encode(summary_sentences, convert_to_tensor=True)
cosine_scores = util.pytorch_cos_sim(summary_embeddings, origin_embedding).cpu().numpy().flatten()


# 数据准确性检查
def check_data_accuracy(origin, summary):
    numbers_origin = re.findall(r'\b\d+\b', origin)
    numbers_summary = re.findall(r'\b\d+\b', summary)
    return len(set(numbers_summary).intersection(set(numbers_origin))) / len(numbers_summary) if numbers_summary else 0


accuracy_scores = np.array([check_data_accuracy(origin_text, sentence) for sentence in summary_sentences])

# 计算综合评分（加权平均）
weights = {'entailment': 0.3, 'cosine': 0.2, 'accuracy': 0.5}
composite_scores = (entailment_scores * weights['entailment'] +
                    cosine_scores * weights['cosine'] +
                    accuracy_scores * weights['accuracy'])

# # 转换为DataFrame并显示结果
# results = [{"sentence": sentence, "entailment_score": entailment, "cosine_score": cosine, "accuracy_score": accuracy,
#             "composite_score": composite}
#            for sentence, entailment, cosine, accuracy, composite in
#            zip(summary_sentences, entailment_scores, cosine_scores, accuracy_scores, composite_scores)]
# df_results = pd.DataFrame(results)
# 转换为DataFrame并显示结果
results = [{"entailment_score": entailment, "cosine_score": cosine, "accuracy_score": accuracy,
            "composite_score": composite}
           for entailment, cosine, accuracy, composite in
           zip(entailment_scores, cosine_scores, accuracy_scores, composite_scores)]
df_results = pd.DataFrame(results)

# 计算段落的整体得分
paragraph_score = np.mean(composite_scores)

# 添加段落整体得分到 DataFrame 中
df_results.loc['Overall'] = [np.mean(entailment_scores), np.mean(cosine_scores), np.mean(accuracy_scores),
                             paragraph_score]

df_results.to_csv('./test.csv')
print(df_results)

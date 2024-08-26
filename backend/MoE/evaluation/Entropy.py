from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import KMeans

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
import numpy as np
from collections import Counter


def calculate_entropy(text):
    words = text.split()
    word_freq = Counter(words)
    total_words = len(words)
    entropy = -sum((freq / total_words) * np.log2(freq / total_words) for freq in word_freq.values())
    return entropy


def calculate_semantic_entropy(text, num_clusters=5):
    sentences = text.split('.')
    embeddings = model.encode(sentences)
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(embeddings)
    labels = kmeans.labels_
    label_freq = Counter(labels)
    total_labels = len(labels)
    entropy = -sum((freq / total_labels) * np.log2(freq / total_labels) for freq in label_freq.values())
    return entropy


original_text = """The axonal arbor data (CA1 neurons) obtained from the ION source reveals the following statistics:
- 'Total Length': the mean value is 72552.47 μm with a standard deviation of 50236.84 μm.
- 'Max Path Distance': the mean value is 9611.74 μm with a standard deviation of 4484.55 μm.
- 'Number of Bifurcations': the mean value is 188.11 with a standard deviation of 184.79.
- 'Center Shift': the mean value is 2254.51 with a standard deviation of 1608.67.
The axonal arbor data (DG neurons) obtained from the ION source reveals the following statistics:
- 'Total Length': the mean value is 5465.07 μm with a standard deviation of 5721.88 μm.
- 'Max Path Distance': the mean value is 2233.0 μm with a standard deviation of 588.99 μm.
- 'Number of Bifurcations': the mean value is 22.47 with a standard deviation of 35.48.
- 'Center Shift': the mean value is 366.76 with a standard deviation of 150.91.
The dendritic arbor data (CA1 neurons) obtained from the ION source reveals the following statistics:
- 'Total Length': the mean value is 7016.85 μm with a standard deviation of 3514.18 μm.
- 'Max Path Distance': the mean value is 956.2 μm with a standard deviation of 659.43 μm.
- 'Number of Bifurcations': the mean value is 44.0 with a standard deviation of 23.99.
- 'Center Shift': the mean value is 173.88 with a standard deviation of 89.05.
The dendritic arbor data (DG neurons) obtained from the ION source reveals the following statistics:
- 'Total Length': the mean value is 3084.22 μm with a standard deviation of 491.72 μm.
- 'Max Path Distance': the mean value is 323.99 μm with a standard deviation of 39.84 μm.
- 'Number of Bifurcations': the mean value is 14.83 with a standard deviation of 2.48.
- 'Center Shift': the mean value is 152.21 with a standard deviation of 39.84."""
summary_text = """he analysis of neuronal morphology data extracted from CA1 and DG neurons, focusing on axonal and dendritic arbors, highlights crucial insights into the structural complexity and spatial distribution of these cells. Notably, 'Total Length' and 'Number of Bifurcations' emerge as paramount features, reflecting the neurons' extensive connectivity and functional versatility.

In CA1 axons, the mean total length reaches 72,552.47 μm, significantly higher than that of DG axons at 54,650.7 μm, indicating a more elaborate axonal network in CA1 neurons. This extensive reach is further emphasized by a mean max path distance of 9,611.74 μm for CA1 axons, dwarfing DG's 2,233.0 μm, suggesting a broader signal transmission capacity in CA1. The number of bifurcations, averaging 188.11 in CA1 axons compared to just 22.47 in DG, reinforces the notion of heightened complexity and potential synaptic contacts in CA1 neurons.

Turning to dendritic arbors, CA1 neurons maintain their intricacy with a mean total length of 7,016.85 μm, surpassing DG’s 3,084.22 μm, reinforcing their capacity for extensive input integration. While both CA1 and DG dendrites show lower values in 'Max Path Distance' and 'Number of Bifurcations' compared to their axonal counterparts, CA1 dendrites still exhibit higher averages, underscoring their complex architecture.

The 'Center Shift' metric, indicative of morphology balance, presents varying degrees but consistently high standard deviations across all neuron types, suggesting a wide range in how evenly distributed these structures are within their environment.

In summary, the profound disparities, particularly in 'Total Length' and 'Number of Bifurcations', between CA1 and DG neurons, underscore the specialized roles these neurons play, with CA1 neurons displaying a more complex and extensive network supportive of their integrative functions in hippocampal circuits. The variability in 'Center Shift' adds another layer of diversity, reflecting the adaptability and heterogeneity of neuronal morphologies in processing and transmitting information.
"""

entropy_original = calculate_entropy(original_text)
entropy_summary = calculate_entropy(summary_text)

print(f"Original Text Entropy: {entropy_original}")
print(f"Summary Text Entropy: {entropy_summary}")

semantic_entropy_original = calculate_semantic_entropy(original_text)
semantic_entropy_summary = calculate_semantic_entropy(summary_text)

print(f"Original Text Semantic Entropy: {semantic_entropy_original}")
print(f"Summary Text Semantic Entropy: {semantic_entropy_summary}")

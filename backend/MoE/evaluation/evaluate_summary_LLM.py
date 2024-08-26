import json
import requests
import re


def split_text(text, max_length=1000):
    """
    Split the text into chunks of a specified maximum length.

    Args:
    text (str): The text to be split.
    max_length (int): The maximum length of each chunk.

    Returns:
    list: A list of text chunks.
    """
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


def summarize_text(summary, origin_input, max_chunk_length=1500):
    """
    Summarize the text and compare with original input.

    Args:
    summary (str): The generated summary text.
    origin_input (str): The original input text.
    max_chunk_length (int): The maximum chunk length for splitting long texts.

    Returns:
    tuple: The evaluation summary and extracted scores.
    """
    evaluation_summary = ""

    # Split the texts into chunks
    summary_chunks = split_text(summary, max_chunk_length)

    for i in range(len(summary_chunks)):
        summary_chunk = summary_chunks[i]

        prompt = f"""
                Evaluate the accuracy of a summary text compared to an original text describing statistical features of a dataset. The original text provides a detailed description of the dataset's statistical features, including various numerical summaries. The summary text condenses the main features from the original text and includes comparative descriptions.

                Please determine whether each statement in the summary text can be accurately inferred from the original text. Focus solely on the correctness and inferability of the summary sentences, without addressing what might be missing or poorly expressed.

                Rate the accuracy of the summary text on a scale from 1 to 10, considering the following aspects:

                1. **Numerical Accuracy**: Assess whether the numerical values mentioned in the summary text are accurate representations of key points from the original text.
                   - **Score Deduction Criteria**:
                     - -1 point for each key numerical value in the summary that is misrepresented (e.g., incorrect ranges or percentages).

                2. **Comparative Descriptions**: Evaluate whether the comparative descriptions in the summary text are logically supported by the original text.
                   - **Score Deduction Criteria**:
                     - -2 points for each comparative statement that cannot be logically derived from the original text.
                     - -1 point for statements that are misleading or lack clarity in their comparison.

                **Scoring Guidelines**:
                - 1 indicates extremely inaccurate.
                - 5 indicates moderately accurate.
                - 10 indicates extremely accurate.

                After rating, provide specific feedback detailing:
                - The key numerical values that were accurately or inaccurately represented.
                - The comparative descriptions that were accurately or inaccurately inferred, explaining the rationale for each deduction.

                Finally, you must output the scores in a dictionary format in the following format: scores = {{'Numerical Accuracy': <score>, 'Comparative Descriptions': <score>}}.

                Summary: {summary_chunk}
                Original Input: {origin_input}
                """

        url = "http://localhost:11434/api/chat"
        headers = {'Content-Type': 'application/json'}
        data = {
            "model": "llama3.1",
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
        try:
            for line in response.iter_lines():
                if line:
                    decoded_line = json.loads(line.decode('utf-8'))
                    if 'message' in decoded_line and 'content' in decoded_line['message']:
                        evaluation_summary += decoded_line['message']['content']
        except json.JSONDecodeError as e:
            print("Error decoding JSON response:", e)
            print("Response content:", response.content)
            return "Error in summarizing text"

    scores = extract_scores(evaluation_summary)
    if scores is None:
        print("No scores found in the evaluation summary. Using default scores.")
        scores = {
            'Accuracy': 0,
            'Consistency': 0,
            'Readability': 0,
            'Conciseness': 0,
        }
    print("scores: \n")
    print(scores)
    return evaluation_summary, scores


def extract_scores(text):
    pattern = r"scores\s*=\s*\{([^}]*)\}"
    match = re.search(pattern, text)
    if match:
        scores_str = "{" + match.group(1) + "}"
        try:
            # Convert the extracted string to a dictionary
            scores_dict = eval(scores_str)
            return scores_dict
        except Exception as e:
            print("Error evaluating scores string:", e)
            return None
    return None


if __name__ == '__main__':
    origin_input = """The queried data comprises 150 neurons extracted from 3 datasets: ION (124 neurons), SEU-ALLEN 
    (18 neurons) and MouseLight (8 neurons). This selection encompasses neuron structures, including axons (150), 
    basal dendrites (74), apical dendrites (5), and local dendrites (0). The queried data locates in left hemisphere 
    (53) and right hemisphere (97). The queried data is distributed across 33 brain regions, detailed as follows:  
    CA1 (24 neurons), DG (24 neurons), AId (10 neurons), ACAd (10 neurons), MOs (9 neurons), PL (9 neurons), 
    CA3 (8 neurons), ORBl (5 neurons), SUB (4 neurons), ORBvl (4 neurons), VPM (4 neurons), FRP (4 neurons), 
    CP (4 neurons), AIv (4 neurons), ProS (3 neurons), ACAv (3 neurons), CLA (2 neurons), ORBm (2 neurons), 
    HATA (2 neurons), PRE (2 neurons), LSv (1 neurons), ILA (1 neurons), SSp-m (1 neurons), RSPagl (1 neurons), 
    MOp (1 neurons), SSp-ll (1 neurons), LGd (1 neurons), SSp-bfd (1 neurons), PO (1 neurons), RSPv (1 neurons), 
    LP (1 neurons), VISrl (1 neurons), and VM (1 neurons). Specifically, there are 68 neurons in cortical layers, 
    including  L5 (35 neurons), L2/3 (19 neurons), L6a (12 neurons), and L1 (2 neurons). """
    summary = "The queried data consists of 150 neurons sourced from three datasets: ION (124 neurons), SEU-ALLEN (18 " \
              "neurons), and MouseLight (8 neurons). These neurons include various structures such as axons (150), " \
              "basal dendrites (74), apical dendrites (5), and no local dendrites. The data is distributed across the " \
              "left hemisphere (53 neurons) and right hemisphere (97 neurons). The neurons are spread across 33 brain " \
              "regions, with the most significant concentrations in CA1 (24 neurons), DG (24 neurons), " \
              "AId (10 neurons), ACAd (10 neurons), MOs (9 neurons), and PL (9 neurons). Additionally, there are 68 " \
              "neurons located in cortical layers, predominantly in L5 (35 neurons), L2/3 (19 neurons), and L6a (12 " \
              "neurons).The queried data consists of 150 neurons sourced from three datasets: ION (124 neurons), " \
              "SEU-ALLEN (18 neurons), and MouseLight (8 neurons). These neurons include various structures such as " \
              "axons (150), basal dendrites (74), apical dendrites (5), and no local dendrites. The data is " \
              "distributed across the left hemisphere (53 neurons) and right hemisphere (97 neurons). The neurons are " \
              "spread across 33 brain regions, with the most significant concentrations in CA1 (24 neurons), " \
              "DG (24 neurons), AId (10 neurons), ACAd (10 neurons), MOs (9 neurons), and PL (9 neurons). " \
              "Additionally, there are 68 neurons located in cortical layers, predominantly in L5 (35 neurons), " \
              "L2/3 (19 neurons), and L6a (12 neurons). "

    evaluation_summary, scores = summarize_text(summary, origin_input)
    print(evaluation_summary)
    print(scores)

import os
import re
import requests
import json
import pandas as pd
import torch
from transformers import GPT2TokenizerFast
from langchain_community.vectorstores import Chroma

gpt4_api_key = ''


# Summarize long texts to reduce token usage
def summarize_text(text, max_length=2000):
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


# detect intent
def predict_intent_gpt4_turbo(query):
    # Construct the prompt
    prompt = f"""As NeuroXiv, an advanced online platform specializing in neuron data visualization and analysis, you offer users the capability to engage in conversations, search for scholarly articles, or navigate through a vast database of neuron data based on specific criteria. Your task is to accurately interpret the intent behind each user query, classifying it into one of the following distinct categories:

    1. 'chat' - This intent should be selected when users are seeking general information about NeuroXiv, its features, or assistance with navigating the website.

    2. 'retrieval' - This intent should be selected when users are seeking information and knowledge about celltypes, neurons and brain regions.

    3. 'article' - Choose this intent when users are explicitly looking for scholarly articles, research papers, or publications related to neuroscience or neuron data.

    4. 'search' - This intent is applicable when users request specific neuron data, datasets, or wish to conduct data searches with certain conditions within the NeuroXiv database.

    It's crucial to focus solely on identifying the correct intent based on the user's query without adding any 
    extraneous details or explanations. Simply return the most appropriate intent from the options provided above. 

    Here are expanded examples for better clarity:

    1. User query: "How can I use NeuroXiv?"
       Intent: chat

    2. User query: "Can you tell me more about your data visualization tools?"
       Intent: chat

    3. User query: "I'm looking for recent articles on synaptic plasticity."
       Intent: article

    4. User query: "Where can I find publications from Dr. Jane Doe on neuroplasticity?"
       Intent: article

    5. User query: "Show me data on neurons in the hippocampus."
       Intent: search

    6. User query: "I need statistical analysis results of dendritic spine density."
       Intent: search

    7. User query: "Compare the differences between MOs and VPM neurons."
       Intent: retrieval

    8. User query: "Compare the projection patterns of VPM and MOp neurons."
       Intent: retrieval

    Remember, the goal is to discern the user's intention with precision, facilitating a more efficient and tailored response that enhances their experience on NeuroXiv. 

    User query: "{query}"

    Intent:
    """

    # Send structured response to the GPT-4 Turbo model
    api_key = gpt4_api_key
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 50,
        "temperature": 0
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    try:
        response_json = response.json()
        return response_json['choices'][0]['message']['content'].strip()
    except KeyError:
        print("Response JSON does not contain 'choices':", response_json)
        raise
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response content:", response.content)
        raise


# Get embeddings
def get_embedding_gpt4_turbo(text):
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        'Authorization': f'Bearer {gpt4_api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "text-embedding-ada-002",  # Change to an appropriate embeddings model if needed
        "input": text
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_json = response.json()
    return response_json['data'][0]['embedding']


# RAG
# Step 1: Load and preprocess Markdown documents
def load_documents_from_directory_gpt4(directory_path):
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".md"):
            with open(os.path.join(directory_path, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                documents.append({"filename": filename, "content": content})
    print(f"Loaded {len(documents)} documents.")
    return documents


def split_document_by_headers_gpt4(content, celltype_name):
    sections = re.split(r"(#{2,3} [^\n]+)", content)
    structured_content = []
    for i in range(0, len(sections) - 1, 2):
        header = sections[i]
        text = sections[i + 1]
        if header.startswith("###"):
            structured_content.append({"title": f"{celltype_name} - {header.strip()}", "text": text.strip()})
        else:
            sub_sections = re.split(r"(### [^\n]+)", text)
            for j in range(0, len(sub_sections) - 1, 2):
                sub_header = sub_sections[j]
                sub_text = sub_sections[j + 1]
                structured_content.append(
                    {"title": f"{celltype_name} - {header.strip()} - {sub_header.strip()}", "text": sub_text.strip()})
    print(f"Processed {len(structured_content)} sections for celltype {celltype_name}.")
    return structured_content


def preprocess_documents_gpt4(directory_path):
    documents = load_documents_from_directory_gpt4(directory_path)
    processed_documents = []
    for doc in documents:
        celltype_name = os.path.splitext(doc['filename'])[0]
        structured_content = split_document_by_headers_gpt4(doc['content'], celltype_name)
        processed_documents.extend(structured_content)
    print(f"Total processed sections: {len(processed_documents)}")
    return processed_documents


# Step 2: Index documents with persistence
def index_documents(processed_documents, persist_directory):
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")  # Use GPT-4 Turbo compatible tokenizer
    tokenizer.add_special_tokens({'pad_token': tokenizer.eos_token})  # Add padding token

    texts = [f"{section['title']} {section['text']}" for section in processed_documents]
    embeddings = []

    for text in texts:
        embedding = get_embedding_gpt4_turbo(text)
        embeddings.append(embedding)

    if not os.path.exists(persist_directory):
        os.makedirs(persist_directory)

    metadata = [{"text": text} for text in texts]
    collection = Chroma(collection_name="docs", persist_directory=persist_directory, embedding_function=None)

    ids = [str(i) for i in range(len(texts))]
    collection._collection.upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadata,
        documents=texts
    )
    collection.persist()
    print(f"Created new vector store with {len(texts)} documents.")

    return collection


# Step 3: Load existing vector store
def load_vectorstore_gpt4(persist_directory):
    if os.path.exists(persist_directory):
        from langchain_community.vectorstores import Chroma
        vectorstore = Chroma(collection_name="docs", persist_directory=persist_directory, embedding_function=None)
        print("Loaded existing vector store.")
        return vectorstore
    else:
        raise FileNotFoundError(f"The directory {persist_directory} does not exist.")


# Step 4: Query documents by celltype and question
def query_documents_by_celltype_and_question(celltype, question, vectorstore, tokenizer, model, num_results=5):
    # Fetch all documents
    all_documents = vectorstore._collection.get(include=["documents", "embeddings", "metadatas"])

    # First, find documents related to the specified celltype
    celltype_documents = []
    celltype_pattern = re.compile(rf"\b{re.escape(celltype)}\b", re.IGNORECASE)
    for doc, embedding, meta in zip(all_documents['documents'], all_documents['embeddings'],
                                    all_documents['metadatas']):
        text = meta['text']
        if celltype_pattern.search(text):
            celltype_documents.append({"text": text, "embedding": embedding})

    if not celltype_documents:
        print(f"No documents found for celltype: {celltype}")
        return []

    print(f"Found {len(celltype_documents)} documents for celltype: {celltype}")

    # Then, perform semantic search within the filtered documents
    query_embedding = get_embedding_gpt4_turbo(question)

    print(
        f"Query embedding: {query_embedding[:10]}...")  # Print first 10 elements of the query embedding for verification

    # Perform similarity search within the filtered documents
    similarities = []
    for doc in celltype_documents:
        doc_embedding = torch.tensor(doc['embedding'])
        similarity = torch.nn.functional.cosine_similarity(torch.tensor(query_embedding), doc_embedding, dim=0)
        similarities.append((similarity.item(), doc['text']))

    similarities.sort(reverse=True, key=lambda x: x[0])
    top_docs = similarities[:num_results]

    print(f"Retrieved {len(top_docs)} documents.")
    for i, (similarity, text) in enumerate(top_docs):
        print(
            f"Document {i + 1}: Similarity: {similarity}, Text: {text[:200]}...")  # Print the first 200 characters of each retrieved document for verification
    return top_docs


# Step 5: Generate answer with data analysis and visualization
def generate_answer_gpt4_turbo(contexts, question):
    # Extract all relevant information from the contexts
    data_points = []
    for context in contexts:
        # Match all key-value pairs
        matches = re.findall(r'(\w+):\s*([\d\.]+)', context)
        if matches:
            data_points.extend(matches)

    # Convert data points to a DataFrame for better manipulation
    if data_points:
        data_df = pd.DataFrame(data_points, columns=['Metric', 'Value'])
    else:
        data_df = pd.DataFrame(columns=['Metric', 'Value'])

    # Summarize each context
    analysis = ""
    for context in contexts:
        analysis += f"- {context[:200]}...\n"  # Summarize each context

    # Create a detailed analysis section
    detailed_analysis = ""
    for i, context in enumerate(contexts):
        detailed_analysis += f"\n### Summary:\n{context[:500]}...\n"

    # Generate a summary of the data points
    data_summary = ""
    if not data_df.empty:
        data_summary = "\n### Key Data Points:\n"
        for metric in data_df['Metric'].unique():
            values = data_df[data_df['Metric'] == metric]['Value']
            avg_value = values.astype(float).mean()
            data_summary += f"- {metric}: {avg_value:.2f} (average from {len(values)} values)\n"

    # Structure the response
    response_intro = "Based on the retrieved documents, here is a detailed analysis:\n\n"
    structured_response = (
            response_intro +
            "### Key Findings:\n" +
            analysis +
            detailed_analysis +
            data_summary +
            "\n\n### Conclusion:\nBased on the data and analysis above, here is the answer to your question. "
            "If some information is missing, the answer also provides related details we could find."
    )

    # Summarize the structured response if it's too long
    summarized_response = summarize_text(structured_response, max_length=2000)

    # Send the structured response to the GPT-4 Turbo model
    api_key = gpt4_api_key
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    prompt = (
        "System: You are an AI assistant. Provide a detailed answer based on the provided context. "
        "Ensure the answer is analytical and uses the data to support the conclusions. "
        "Structure the answer in clear sections, including an introduction, key findings, and a conclusion. "
        "If some relevant information is missing, summarize what you do know based on the context provided.\n\n"
        f"User: {question}\n\n"
        f"Context: {summarized_response}\n\n"
    )
    data = {
        "model": "gpt-4-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096,
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    try:
        response_json = response.json()
        print(response_json)
        return response_json['choices'][0]['message']['content'].strip()
    except KeyError:
        print("Response JSON does not contain 'choices':", response_json)
        raise
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response content:", response.content)
        raise


def extract_celltypes_from_question_gpt4(question, available_celltypes):
    # Extract words from the question
    words = re.findall(r"\b[A-Za-z0-9\-]+\b", question)
    # Find the intersection between extracted words and available celltypes
    celltypes = list(set(words) & set(available_celltypes))
    return celltypes


def AIPOM_gpt4_turbo(query):
    directory_path = r"D:\NeuroXiv\api\knowledge_base(1)\knowledge_base"
    persist_directory = "D:/NeuroXiv/api/LLM/MarkDownDB_GPT4"
    question = query
    reindex = False  # Set to True to reindex documents, False to use existing index

    if reindex:
        print('reindex')
        processed_documents = preprocess_documents_gpt4(directory_path)
        vectorstore = index_documents(processed_documents, persist_directory)
    else:
        vectorstore = load_vectorstore_gpt4(persist_directory)

    available_celltypes = [os.path.splitext(f)[0] for f in os.listdir(directory_path) if f.endswith(".md")]
    print(f"Available celltypes: {available_celltypes}")

    celltypes = extract_celltypes_from_question_gpt4(question, available_celltypes)
    print(f"Extracted celltypes: {celltypes}")
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")  # Use GPT-4 Turbo compatible tokenizer
    tokenizer.add_special_tokens({'pad_token': tokenizer.eos_token})  # Add padding token

    results = []
    for celltype in celltypes:
        docs = query_documents_by_celltype_and_question(celltype, question, vectorstore, tokenizer, None)
        results.extend(docs)

    if results:
        relevant_texts = [result[1] for result in results]
        answer = generate_answer_gpt4_turbo(relevant_texts[:3], question)  # Limit to top 5 relevant texts
        print("Final Answer:", answer)
        return answer
    else:
        # If no relevant documents are found, return a meaningful response
        return "Based on the current knowledge base, there are no specific documents related to your query. " \
               "However, here are some general details about the topic: [Provide some general information or guidance]"


if __name__ == "__main__":
    query = "compare the projection patterns between VPM and MOp neurons"
    AIPOM_gpt4_turbo(query)

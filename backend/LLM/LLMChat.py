import json
import os

import requests
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

gpt4_api_key = ''


def chatWithLLM(querry):
    print(querry)
    llama3 = os.environ.get("MODEL", "llama3")
    l_embeddings_model_name = "D:/NeuroXiv/api/all-mpnet-base-v2"
    l_persist_directory = "D:/NeuroXiv/api/LLM/NeuroxivInfo"
    l_target_source_chunks = 5
    model_kwargs = {'device': 'cuda:0'}
    # 创建一个包含编码选项的字典，具体设置 'normalize_embeddings' 为 False
    encode_kwargs = {'normalize_embeddings': False}
    embeddings = HuggingFaceEmbeddings(model_name=l_embeddings_model_name, model_kwargs=model_kwargs,
                                       encode_kwargs=encode_kwargs)
    db = Chroma(persist_directory=l_persist_directory, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": l_target_source_chunks})
    related_info = retriever.invoke(querry)

    api_key = gpt4_api_key
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    prompt = (
        "System: You are an AI assistant. Provide a detailed answer based on the provided context. "
        "Ensure the answer is analytical and uses the provided context to generate the conclusions. "
        "If some relevant information is missing, summarize what you do know based on the context provided.\n\n"
        f"User: {querry}\n\n"
        f"Context: {related_info}\n\n"
    )
    data = {
        "model": "gpt-4-turbo",
        "messages": [{"role": "user", "content": prompt}],
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    try:
        response_json = response.json()
        print(response_json['choices'][0]['message']['content'].strip())
        return response_json['choices'][0]['message']['content'].strip()
    except KeyError:
        print("Response JSON does not contain 'choices':", response_json)
        raise
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response content:", response.content)
        raise


if __name__ == "__main__":
    query = "how can i search neurons"
    chatWithLLM(query)

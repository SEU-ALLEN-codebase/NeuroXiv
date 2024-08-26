#!/usr/bin/env python3
import os
import glob
from typing import List
from multiprocessing import Pool

import torch
from tqdm import tqdm

from langchain_community.document_loaders import (
    CSVLoader,
    EverNoteLoader,
    PyMuPDFLoader,
    TextLoader,
    UnstructuredEmailLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from constants import CHROMA_SETTINGS

# Load environment variables
persist_directory = os.environ.get('PERSIST_DIRECTORY', 'LLMDB')
print(persist_directory)
source_directory = os.environ.get('SOURCE_DIRECTORY', 'source_documents')
embeddings_model_name = os.environ.get('EMBEDDINGS_MODEL_NAME', 'sentence-transformers/all-MiniLM-L6-v2')
chunk_size = 500
chunk_overlap = 0


# Custom document loaders
class MyElmLoader(UnstructuredEmailLoader):
    """Wrapper to fallback to text/plain when default does not work"""

    def load(self) -> List[Document]:
        """Wrapper adding fallback for elm without html"""
        try:
            try:
                doc = UnstructuredEmailLoader.load(self)
            except ValueError as e:
                if 'text/html content not found in email' in str(e):
                    # Try plain text
                    self.unstructured_kwargs["content_source"] = "text/plain"
                    doc = UnstructuredEmailLoader.load(self)
                else:
                    raise
        except Exception as e:
            # Add file_path to exception message
            raise type(e)(f"{self.file_path}: {e}") from e

        return doc


# Map file extensions to document loaders and their arguments
LOADER_MAPPING = {
    ".csv": (CSVLoader, {}),
    # ".docx": (Docx2txtLoader, {}),
    ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".eml": (MyElmLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (TextLoader, {"encoding": "utf8"}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PyMuPDFLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
    # Add more mappings for other file extensions and loaders as needed
}


def load_single_document(file_path: str) -> List[Document]:
    ext = "." + file_path.rsplit(".", 1)[-1]
    if ext in LOADER_MAPPING:
        loader_class, loader_args = LOADER_MAPPING[ext]
        loader = loader_class(file_path, **loader_args)
        return loader.load()

    raise ValueError(f"Unsupported file extension '{ext}'")


def load_documents(source_dir: str, ignored_files: List[str] = []) -> List[Document]:
    """
    Loads all documents from the source documents directory, ignoring specified files
    """
    all_files = []
    for ext in LOADER_MAPPING:
        all_files.extend(
            glob.glob(os.path.join(source_dir, f"**/*{ext}"), recursive=True)
        )
    filtered_files = [file_path for file_path in all_files if file_path not in ignored_files]

    with Pool(processes=os.cpu_count()) as pool:
        results = []
        with tqdm(total=len(filtered_files), desc='Loading new documents', ncols=80) as pbar:
            for i, docs in enumerate(pool.imap_unordered(load_single_document, filtered_files)):
                results.extend(docs)
                pbar.update()

    return results


def process_documents(ignored_files: List[str] = []) -> List[Document]:
    """
    Load documents and split in chunks
    """
    print(f"Loading documents from {source_directory}")
    documents = load_documents(source_directory, ignored_files)
    if not documents:
        print("No new documents to load")
        exit(0)
    print(f"Loaded {len(documents)} new documents from {source_directory}")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} chunks of text (max. {chunk_size} tokens each)")
    return texts


def process_MD_documents(ignored_files: List[str] = []) -> List[Document]:
    """
    Load documents and split in chunks
    """
    print(f"Loading documents from {source_directory}")
    documents = load_documents(source_directory, ignored_files)
    if not documents:
        print("No new documents to load")
        exit(0)
    print(f"Loaded {len(documents)} new documents from {source_directory}")
    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    texts = []
    MD_Spliter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=False)
    for doc in documents:
        # print(doc)
        text = MD_Spliter.split_text(doc.page_content)
        texts.extend(text)
    print(texts)
    print(f"Split into {len(texts)} ")
    return texts


def does_vectorstore_exist(persist_directory: str) -> bool:
    """
    Checks if vectorstore exists
    """
    if os.path.exists(os.path.join(persist_directory, 'index')):
        if os.path.exists(os.path.join(persist_directory, 'chroma-collections.parquet')) and os.path.exists(
                os.path.join(persist_directory, 'chroma-embeddings.parquet')):
            list_index_files = glob.glob(os.path.join(persist_directory, 'index/*.bin'))
            list_index_files += glob.glob(os.path.join(persist_directory, 'index/*.pkl'))
            # At least 3 documents are needed in a working vectorstore
            if len(list_index_files) > 3:
                return True
    return False


def encode_and_add_in_batches(texts, db, batch_size=41666):
    """
    分批创建嵌入并将它们添加到数据库中。

    :param texts: 待处理的文本列表。
    :param db: Chroma数据库实例，用于添加文档和嵌入。
    :param batch_size: 每批处理的文本数量，不超过41,666。
    """
    num_batches = len(texts) // batch_size + (1 if len(texts) % batch_size > 0 else 0)
    print(f"Processing {len(texts)} texts in {num_batches} batches...")

    for batch_index in range(num_batches):
        start_index = batch_index * batch_size
        end_index = min(start_index + batch_size, len(texts))
        current_batch_texts = texts[start_index:end_index]

        # 注意：这里我们直接将文本的批次添加到数据库中，假设db.add_documents方法内部处理嵌入的创建
        print(f"Adding batch {batch_index + 1}/{num_batches} to database...")
        db.add_documents(current_batch_texts)
        print(f"Batch {batch_index + 1} added to database.")


# def main():
#     print('torch.cuda')
#     print(torch.cuda.is_available())
#     # Create embeddings with potential GPU support
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     print(f"Using device: {device}")
#     l_embeddings_model_name = "D:/NeuroXiv/api/all-mpnet-base-v2"
#     l_persist_directory = "D:/NeuroXiv/api/LLM/LLMDB"
#     # 创建一个包含模型配置选项的字典，指定使用GPU进行计算
#     model_kwargs = {'device': 'cuda:0'}
#
#     # 创建一个包含编码选项的字典，具体设置 'normalize_embeddings' 为 False
#     encode_kwargs = {'normalize_embeddings': False}
#     embeddings = HuggingFaceEmbeddings(model_name=l_embeddings_model_name, model_kwargs=model_kwargs,
#                                        encode_kwargs=encode_kwargs)
#
#     texts = process_documents()
#
#     if does_vectorstore_exist(persist_directory):
#         print(f"Appending to existing vectorstore at {l_persist_directory}")
#         db = Chroma(persist_directory=l_persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS)
#         collection = db.get()
#         ignored_files = [metadata['source'] for metadata in collection['metadatas']]
#         additional_texts = process_documents(ignored_files)
#         print(f"Creating embeddings for additional texts. May take some minutes...")
#         # encode_and_add_in_batches(additional_texts, db, batch_size=41666)
#         encode_and_add_in_batches(additional_texts, db, batch_size=500)
#     else:
#         print("Creating new vectorstore")
#         print(f"Processing and creating embeddings for all documents. This may take some time...")
#         # 使用修改后的函数来分批处理和创建新的vectorstore
#         db = None
#         # batch_size = 41666  # 确保不超过限制
#         batch_size = 500  # 确保不超过限制
#         for start_idx in range(0, len(texts), batch_size):
#             end_idx = start_idx + batch_size
#             batch_texts = texts[start_idx:end_idx]
#             if db is None:
#                 db = Chroma.from_documents(batch_texts, embeddings, persist_directory=l_persist_directory,
#                                            client_settings=CHROMA_SETTINGS)
#             else:
#                 db.add_documents(batch_texts)
#
#     if db is not None:
#         db.persist()
#     print(f"Ingestion complete! You can now run privateGPT.py to query your documents")

# def main():
#     print('torch.cuda')
#     print(torch.cuda.is_available())
#     # Create embeddings with potential GPU support
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     print(f"Using device: {device}")
#     l_embeddings_model_name = "D:/NeuroXiv/api/all-MiniLM-L6-v2"
#     # 创建一个包含模型配置选项的字典，指定使用GPU进行计算
#     model_kwargs = {'device': 'cuda:0'}
#
#     # 创建一个包含编码选项的字典，具体设置 'normalize_embeddings' 为 False
#     encode_kwargs = {'normalize_embeddings': False}
#     embeddings = HuggingFaceEmbeddings(model_name=l_embeddings_model_name, model_kwargs=model_kwargs,
#                                        encode_kwargs=encode_kwargs)
#
#     # # 检查CUDA是否可用，并将模型移至GPU
#     # if torch.cuda.is_available():
#     #     embeddings.model.to('cuda')
#
#     if does_vectorstore_exist(persist_directory):
#         print(f"Appending to existing vectorstore at {persist_directory}")
#         db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS)
#         collection = db.get()
#         texts = process_documents([metadata['source'] for metadata in collection['metadatas']])
#         print(f"Creating embeddings. May take some minutes...")
#         db.add_documents(texts)
#     else:
#         print("Creating new vectorstore")
#         texts = process_documents()
#         print(f"Creating embeddings. May take some minutes...")
#         db = Chroma.from_documents(texts, embeddings, persist_directory=persist_directory)
#     db.persist()
#     db = None
#
#     print(f"Ingestion complete! You can now run privateGPT.py to query your documents")

def main():
    l_persist_directory = os.environ.get('PERSIST_DIRECTORY', 'NeuroxivInfo')
    print(torch.cuda.is_available())
    # Create embeddings with potential GPU support
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    l_embeddings_model_name = "D:/NeuroXiv/api/all-mpnet-base-v2"
    # 创建一个包含模型配置选项的字典，指定使用GPU进行计算
    model_kwargs = {'device': 'cuda:0'}

    # 创建一个包含编码选项的字典，具体设置 'normalize_embeddings' 为 False
    encode_kwargs = {'normalize_embeddings': False}
    embeddings = HuggingFaceEmbeddings(model_name=l_embeddings_model_name, model_kwargs=model_kwargs,
                                       encode_kwargs=encode_kwargs)

    # # 检查CUDA是否可用，并将模型移至GPU
    # if torch.cuda.is_available():
    #     embeddings.model.to('cuda')

    if does_vectorstore_exist(l_persist_directory):
        print(f"Appending to existing vectorstore at {l_persist_directory}")
        db = Chroma(persist_directory=l_persist_directory, embedding_function=embeddings,
                    client_settings=CHROMA_SETTINGS)
        collection = db.get()
        texts = process_documents([metadata['source'] for metadata in collection['metadatas']])
        print(f"Creating embeddings. May take some minutes...")
        db.add_documents(texts)
    else:
        print("Creating new vectorstore")
        texts = process_documents()
        print(f"Creating embeddings. May take some minutes...")
        db = Chroma.from_documents(texts, embeddings, persist_directory=l_persist_directory)
    db.persist()
    db = None

    print(f"Ingestion complete! You can now run privateGPT.py to query your documents")


if __name__ == "__main__":
    main()

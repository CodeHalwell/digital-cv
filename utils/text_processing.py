from __future__ import annotations

from typing import Iterable, Sequence

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.text import TextLoader
import os
import dotenv
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.vector_db import VectorDB

dotenv.load_dotenv()

class DocumentProcessing:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large", api_key=os.getenv("OPENAI_API_KEY")
        )
        self.vector_db = VectorDB(embedding_model=self.embeddings)

    def split_text(self, document):
        """Split document text into chunks"""
        if isinstance(document, list):
            # Handle list of documents from loaders
            all_texts = []
            for doc in document:
                texts = self.text_splitter.split_text(doc.page_content)
                all_texts.extend(texts)
            return all_texts
        else:
            # Handle raw text string
            texts = self.text_splitter.split_text(document)
            return texts

    def embed_text(self, texts: Sequence[str]):
        """Generate embeddings for text chunks."""
        return self.embeddings.embed_documents(list(texts))

    def create_vector_db(self, texts, metadata=None):
        """Add texts to vector database"""
        if metadata is None:
            metadata = [{"source": "unknown"} for _ in texts]
        
        embeddings = self.embed_text(texts)

        # Create documents with IDs
        documents = list(texts)
        metadatas = list(metadata)
        ids = [f"doc_{i}" for i in range(len(documents))]

        self.vector_db.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings,
        )

    def create_vector_db_from_file(self, file_path):
        """Process a single file and add to vector database"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith(".txt"):
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
        
        documents = loader.load()
        texts = self.split_text(documents)
        
        # Create metadata for each chunk
        metadata = [{"source": file_path, "chunk_id": i} for i in range(len(texts))]
        
        self.create_vector_db(texts, metadata)
        return self.vector_db

    def create_vector_db_from_directory(self, directory_path):
        """Process all supported files in a directory"""
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
            
        supported_extensions = [".pdf", ".txt"]
        processed_files = 0
        
        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
                
            # Check if file has supported extension
            if any(file.endswith(ext) for ext in supported_extensions):
                try:
                    self.create_vector_db_from_file(file_path)
                    processed_files += 1
                    print(f"Processed: {file}")
                except Exception as e:
                    print(f"Error processing {file}: {str(e)}")
            else:
                print(f"Skipping unsupported file type: {file}")
        
        print(f"Successfully processed {processed_files} files")
        return self.vector_db
        
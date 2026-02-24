import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import List, Dict, Any
import os
import numpy as np
from config import Config


class SimpleEmbeddings:
    """Lightweight local embeddings using character n-gram hashing (no server needed)"""

    EMBEDDING_DIM = 768

    def _get_embedding(self, text: str) -> List[float]:
        """Generate a deterministic embedding from text using hashing"""
        text = text.lower()
        vec = np.zeros(self.EMBEDDING_DIM)
        for i in range(len(text) - 2):
            trigram = text[i:i + 3]
            h = hash(trigram) % self.EMBEDDING_DIM
            vec[h] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._get_embedding(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._get_embedding(text)


class RAGSystem:
    """RAG system using ChromaDB with lightweight local embeddings"""

    def __init__(self):
        self.embeddings = SimpleEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
        )
        self.vectorstore = None
        self.documents = []

    def process_documents(self, text: str) -> List[Document]:
        """Process and split documents into chunks"""
        chunks = self.text_splitter.split_text(text)
        documents = [
            Document(page_content=chunk, metadata={"source": "uploaded_document"})
            for chunk in chunks
        ]
        self.documents = documents
        return documents

    def create_vectorstore(self, documents: List[Document]):
        """Create and store documents in ChromaDB vectorstore"""
        try:
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=Config.CHROMA_PERSIST_DIR
            )
        except Exception as e:
            raise Exception(f"Error creating vectorstore: {str(e)}")

    def search_similar_chunks(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar document chunks based on query"""
        if not self.vectorstore:
            raise Exception("Vectorstore not initialized. Please process documents first.")
        try:
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            raise Exception(f"Error searching vectorstore: {str(e)}")

    def get_context_for_mcq(self, num_questions: int = 10) -> List[str]:
        """Get diverse context chunks for MCQ generation"""
        if not self.documents:
            raise Exception("No documents processed yet.")

        selected_chunks = []
        total_chunks = len(self.documents)

        if num_questions <= total_chunks:
            step = total_chunks // num_questions
            for i in range(0, total_chunks, step):
                if len(selected_chunks) < num_questions:
                    selected_chunks.append(self.documents[i].page_content)
        else:
            selected_chunks = [doc.page_content for doc in self.documents]

        return selected_chunks[:num_questions]

    def clear_vectorstore(self):
        """Clear the vectorstore and documents"""
        if self.vectorstore:
            try:
                import shutil
                if os.path.exists(Config.CHROMA_PERSIST_DIR):
                    shutil.rmtree(Config.CHROMA_PERSIST_DIR)
                self.vectorstore = None
                self.documents = []
            except Exception as e:
                print(f"Error clearing vectorstore: {str(e)}")

    def get_document_summary(self) -> Dict[str, Any]:
        """Get summary information about processed documents"""
        if not self.documents:
            return {"total_chunks": 0, "total_characters": 0}

        total_chunks = len(self.documents)
        total_characters = sum(len(doc.page_content) for doc in self.documents)

        return {
            "total_chunks": total_chunks,
            "total_characters": total_characters,
            "average_chunk_length": total_characters // total_chunks if total_chunks > 0 else 0
        }

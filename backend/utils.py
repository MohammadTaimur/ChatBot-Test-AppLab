from fastapi import HTTPException
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import faiss, numpy as np, pickle
from sentence_transformers import SentenceTransformer
from typing import List

def chunking_text(text: str) -> List[str]:
    """
    Splits the given text into chunks for processing.

    Parameters:
    - text (str): The input text to split into chunks.

    Returns:
    - List[str]: A list of text chunks.
    - HTTPException: If an error occurs during text chunking.
    """
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50) #Setting a chunk size at 500 characters with an overlap of 50
        return splitter.split_text(text)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Error Chunking Text/PDF: {e}")

# Load embedding model once
try:
    embedding_model = SentenceTransformer("all-MiniLM-L6-V2")
except Exception as e:
    raise HTTPException(status_code=404, detail=f"Embedding model could not be loaded: {e}")

# Paths for saving FAISS + metadata
faiss_index_path = "faiss_store.index"
metadata_path = "faiss_metadata.pkl"


def build_faiss_index(chunks):
    """
    Build and save a FAISS index for the given chunks.
    """
    try:
        embeddings = np.array([embedding_model.encode(chunk) for chunk in chunks], dtype=np.float32)

        # Create index
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)

        # Save FAISS index
        faiss.write_index(index, faiss_index_path)

        # Save metadata (docs)
        with open(metadata_path, "wb") as f:
            pickle.dump(chunks, f)

        print("✅ FAISS index built and saved.")
    except Exception as e:
        raise HTTPException(status_code=402, detail=f"Error creating FAISS index: {e}")


def retrieve_relevant_text(query: str, top_k: int = 3):
    """
    Retrieve the most relevant chunks from FAISS for a query.
    """
    try:
        # Load FAISS + metadata
        index = faiss.read_index(faiss_index_path)
        with open(metadata_path, "rb") as f:
            documents = pickle.load(f)

        # Encode query
        query_embedding = np.array([embedding_model.encode(query)], dtype=np.float32)

        # Search
        distances, indices = index.search(query_embedding, top_k)

        retrieved_docs = [documents[i] for i in indices[0] if i < len(documents)]

        if retrieved_docs:
            return "\n---\n".join(retrieved_docs)
        else:
            return "No relevant information found."
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Error retrieving from FAISS: {e}")
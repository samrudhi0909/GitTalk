from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

def generate_embeddings(documents):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(documents, convert_to_numpy=True, show_progress_bar=True)
    return embeddings, model

def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index
import os
import shutil
from git import Repo
from openai import OpenAI
from pinecone import Pinecone,ServerlessSpec, Index
import streamlit as st
import tiktoken
from sentence_transformers import SentenceTransformer
import google.generativeai as genai


# Initialize OpenAI and Pinecone API keys

pc = Pinecone(api_key=st.secrets["pinecone"]["api_key"])
genai.configure(api_key=st.secrets["gemini"]["api_key"])

def clone_repository(repo_url, clone_path='./repo'):
    if os.path.exists(clone_path):
        # Remove existing repository folder
        shutil.rmtree(clone_path)
    try:
        Repo.clone_from(repo_url, clone_path)
        print(f"Repository cloned to {clone_path}")
    except Exception as e:
        print(f"Error cloning repository: {e}")



def split_text(text, max_tokens=500):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk = tokens[i:i+max_tokens]
        chunks.append(tokenizer.decode(chunk))
    return chunks

def process_repository(clone_path='./repo'):
    code_texts = []
    for root, dirs, files in os.walk(clone_path):
        for file in files:
            if file.endswith(('.py', '.js', '.java', '.c', '.cpp', '.rb', '.go', '.ts', '.cs', '.php', '.swift')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as f:
                        # Check if file is text-based
                        text = f.read().decode('utf-8', errors='ignore')
                        chunks = split_text(text)
                        code_texts.extend(chunks)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return code_texts


embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_embedding(text):
    return embedding_model.encode(text).tolist()  # Returns 384-dim vector

def generate_and_store_embeddings(texts, index_name):
    # Delete existing index if needed
    if index_name in pc.list_indexes().names():
        pc.delete_index(index_name)
    
    # Create new index with free-tier config
    pc.create_index(
        name=index_name,
        dimension=384,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )
    
    # Wait for index to initialize
    import time
    time.sleep(30)  # Free tier needs longer initialization
    
    # Access the index CORRECTLY
    index = pc.Index(index_name)  # <-- Fix here
    
    # Process batches
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        embeddings = [get_embedding(text) for text in batch_texts]
        metadata = [{'text': text} for text in batch_texts]
        ids = [str(idx) for idx in range(i, i + len(batch_texts))]
        
        vectors = [
            {'id': id_, 'values': embedding, 'metadata': meta}
            for id_, embedding, meta in zip(ids, embeddings, metadata)
        ]
        
        index.upsert(vectors=vectors)
        print(f'Indexed texts {i} to {i + len(batch_texts)}')

def retrieve_relevant_chunks(query, index_name, top_k=5):
    index_name = sanitize_index_name(index_name)
    if index_name not in pc.list_indexes().names():
      raise ValueError(f"Index '{index_name}' does not exist. Process the repository first!")
      
    query_embedding = get_embedding(query)
    index = pc.Index(index_name)  
    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    contexts = [match.metadata['text'] for match in result.matches]
    return contexts



def generate_answer(contexts, question):
    context_text = "\n\n".join(contexts)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(
        f"Context:\n{context_text}\n\nQuestion: {question}"
    )
    return response.text

def sanitize_index_name(repo_url):
    # Extract base name and clean it
    name = repo_url.split('/')[-1].replace('.git', '').lower()
  
    name = ''.join([c if c.isalnum() else '-' for c in name])
  
 
    name = name.strip('-')[:45]
    
    # Handle empty edge case
    return name or "default-index"

# Streamlit App Code

def main():
    st.title("GitHub Repository Q&A Assistant")

    # Input for GitHub repository URL
    repo_url = st.text_input("Enter the GitHub repository URL:")

    if st.button("Process Repository") and repo_url:
        with st.spinner('Cloning and processing the repository...'):
            clone_repository(repo_url)
            code_texts = process_repository()
            # Use a unique index name based on the repository URL
            index_name = sanitize_index_name(repo_url)
            generate_and_store_embeddings(code_texts, index_name)
        st.success('Repository processed successfully!')

    # Input for the user's question
    question = st.text_input("Ask a question about the repository:")

    if st.button("Get Answer") and question and repo_url:
        with st.spinner('Generating answer...'):
            index_name = repo_url.split('/')[-1].replace('.git', '').replace('.', '_')
            contexts = retrieve_relevant_chunks(question, index_name)
            answer = generate_answer(contexts, question)
        st.write("**Answer:**")
        st.write(answer)

if __name__ == "__main__":
    main()
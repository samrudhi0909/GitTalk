from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from utils.data_processing import clone_repo, read_code_files
from utils.embeddings import generate_embeddings, create_faiss_index
from utils.models import get_answer

app = Flask(__name__)
CORS(app)

# Global variables to store data
code_contents = []
embeddings = None
embed_model = None
index = None
qa_pipeline = None

@app.route('/api/fetch-repo', methods=['POST'])
def fetch_repo():
    global code_contents, embeddings, embed_model, index, qa_pipeline
    data = request.get_json()
    repo_url = data.get('repoUrl')
    if not repo_url:
        return jsonify({'error': 'Repository URL is required.'}), 400
    try:
        # Clone repository
        repo_dir = clone_repo(repo_url)
        # Read code files
        code_contents = read_code_files(repo_dir)
        # Generate embeddings
        embeddings, embed_model = generate_embeddings(code_contents)
        # Create FAISS index
        index = create_faiss_index(embeddings)
        # Load QA model
        qa_pipeline = get_answer.load_qa_model()
        return jsonify({'message': 'Repository processed successfully.'}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to process repository.'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    global code_contents, embeddings, embed_model, index, qa_pipeline
    data = request.get_json()
    question = data.get('message')
    if not question:
        return jsonify({'error': 'Question is required.'}), 400
    if not index or not qa_pipeline:
        return jsonify({'error': 'Repository not processed yet.'}), 400
    try:
        answer = get_answer.get_answer(
            question, index, code_contents, embed_model, qa_pipeline
        )
        return jsonify({'reply': answer}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to generate answer.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
from transformers import pipeline

class get_answer:
    @staticmethod
    def load_qa_model():
        qa_pipeline = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')
        return qa_pipeline

    @staticmethod
    def get_answer(question, index, code_contents, embed_model, qa_pipeline):
        question_embedding = embed_model.encode([question], convert_to_numpy=True)
        distances, indices = index.search(question_embedding, k=5)
        relevant_snippets = [code_contents[idx] for idx in indices[0]]
        context = '\n'.join(relevant_snippets)
        try:
            answer = qa_pipeline({'context': context, 'question': question})
            return answer['answer']
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "I'm sorry, I couldn't find an answer to your question."
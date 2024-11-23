from flask import Flask, request, jsonify
from flask_cors import CORS
from password_utils import (classify_password, check_password_similarity, rule_based_feedback,
                            generate_secure_suggestions, load_models_and_data)

app = Flask(__name__)
CORS(app) 

# Load models on start
models_and_data = load_models_and_data()

@app.route('/analyze_password', methods=['POST'])
def analyze_password():
    data = request.json
    password = data['password']
    roberta_model, roberta_tokenizer, fasttext_model, compromised_embeddings, compromised_passwords = models_and_data

    strength = classify_password(password, roberta_model, roberta_tokenizer)
    similarity_info = check_password_similarity(password, fasttext_model, compromised_embeddings, compromised_passwords)
    feedback = rule_based_feedback(password, similarity_info[2])  # Using status for feedback

    response = {
        "strength": strength,
        "similarity": similarity_info,
        "feedback": feedback
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

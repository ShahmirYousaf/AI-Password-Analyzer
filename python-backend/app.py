from flask import Flask, request, jsonify
from flask_cors import CORS

from password_functions import *

app = Flask(__name__)
CORS(app)  



@app.route('/analyze_password', methods=['POST'])
def analyze_password():
    data = request.get_json()
    input_password = data['password']
    
    
    strength = classify_password(input_password, roberta_model, roberta_tokenizer)
    most_similar_password, similarity_percentage, status, lowest_distance = check_password_similarity(
        input_password, fasttext_model, compromised_embeddings, compromised_passwords
    )
    feedback = rule_based_feedback(input_password, status)
    suggestions = generate_secure_suggestions(
        input_password, fasttext_model, compromised_embeddings, compromised_passwords
    ) if status != "Password Safe" else []

    return jsonify({
        'input_password': input_password,
        'strength': strength,
        'most_similar_password': most_similar_password,
        'levenshtein_distance': f"{lowest_distance:.2f}%",
        'status': status,
        'feedback': feedback,
        'suggestions': suggestions
    })

if __name__ == '__main__':
    app.run(debug=True) 
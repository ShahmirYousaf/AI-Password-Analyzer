import random
import string
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import fasttext
import torchclear
import Levenshtein
import re

# Function to load models and data required for analysis
def load_models_and_data():
    roberta_model = RobertaForSequenceClassification.from_pretrained("./password_strength_roberta")
    roberta_tokenizer = RobertaTokenizer.from_pretrained("./password_strength_roberta")
    fasttext_model = fasttext.load_model("fasttext_rockyou.bin")
    compromised_embeddings = np.load("rockyou_embeddings.npy", allow_pickle=True)
    with open("rockyou.txt", "r", encoding="latin1") as f:
        compromised_passwords = [line.strip() for line in f]
    return roberta_model, roberta_tokenizer, fasttext_model, compromised_embeddings, compromised_passwords

# Classify password strength using RoBERTa model
def classify_password(password, roberta_model, roberta_tokenizer):
    inputs = roberta_tokenizer(password, return_tensors="pt", truncation=True, padding=True, max_length=32)
    outputs = roberta_model(**inputs)
    predicted_class = torch.argmax(outputs.logits, dim=1).item()
    labels = ["Weak", "Moderate", "Strong"]
    return labels[predicted_class]

# Check similarity against precomputed embeddings using FastText model
def check_password_similarity(input_password, fasttext_model, compromised_embeddings, compromised_passwords, top_n=100):
    input_embedding = fasttext_model.get_sentence_vector(input_password)

    print("\nComputing similarities...")
    similarities = cosine_similarity([input_embedding], compromised_embeddings)[0]

    # Shortlist top-n candidates for Levenshtein distance calculation
    top_indices = similarities.argsort()[-top_n:][::-1]
    shortlisted_passwords = [compromised_passwords[i] for i in top_indices]

    print("\nComputing Levenshtein distances...")
    best_password = None
    lowest_distance = float('inf')
    for candidate in tqdm(shortlisted_passwords, desc="Processing candidates"):
        distance = Levenshtein.distance(input_password, candidate) / max(len(input_password), len(candidate))
        if distance < lowest_distance:
            lowest_distance = distance
            best_password = candidate

    similarity_percentage = max(similarities) * 100
    status = "Password Compromised" if lowest_distance < 0.7 else "Password Safe"

    return best_password, similarity_percentage, status, (1 - lowest_distance) * 100  # Convert to percentage

# Provide rule-based feedback on password strength
def rule_based_feedback(password, status):
    if status == "Password Safe":
        return "Your password is strong and safe to use. No changes required!"

    feedback = []
    # Check for length
    if len(password) < 8:
        feedback.append("Your password is too short. Use at least 8 characters.")

    # Check for character diversity
    if not any(char.isupper() for char in password):
        feedback.append("Add at least one uppercase letter.")
    if not any(char.islower() for char in password):
        feedback.append("Add at least one lowercase letter.")
    if not any(char.isdigit() for char in password):
        feedback.append("Include at least one number.")
    if not any(char in "!@#$%^&*()_+[]{}|;:,.<>?/`~" for char in password):
        feedback.append("Add at least one special character (e.g., !, @, #, $).")

    # Check for common patterns
    if re.search(r"(password|1234|abcd|qwerty|admin)", password, re.IGNORECASE):
        feedback.append("Avoid using common patterns or dictionary words like 'password', '1234', or 'qwerty'.")

    # Check for repetitive characters
    if re.search(r"(.)\1{2,}", password):
        feedback.append("Avoid repetitive characters like 'aaa' or '111'.")

    return " ".join(feedback)

# Enhance password by adding random elements to it
def enhance_password(password):
    special_characters = "!@#$%^&*"
    enhanced_password = list(password)

    # Slightly modify characters to retain structure
    for i in range(len(enhanced_password)):
        if random.random() < 0.1:  # 10% chance to replace
            enhanced_password[i] = random.choice(special_characters)
        elif random.random() < 0.3:  # 30% chance to change case
            enhanced_password[i] = enhanced_password[i].swapcase()

    # Add random characters at the beginning and end
    enhanced_password.insert(0, random.choice(special_characters))
    enhanced_password.append(random.choice(special_characters))
    enhanced_password.append(str(random.randint(10, 99)))

    # Ensure the password is at least 8 characters long
    while len(enhanced_password) < 8:
        enhanced_password.append(random.choice(string.ascii_letters).upper())

    return "".join(enhanced_password)

# Check if password is safe using Levenshtein distance
def is_password_safe_with_levenshtein(password, compromised_passwords, threshold=0.7):
    for compromised_password in compromised_passwords:
        distance = Levenshtein.distance(password, compromised_password) / max(len(password), len(compromised_password))
        if distance < threshold:
            return False, distance * 100  # Convert to percentage
    return True, None

# Generate secure password suggestions
def generate_secure_suggestions(password, fasttext_model, compromised_embeddings, compromised_passwords, num_suggestions=3):
    suggestions = []
    print("\nGenerating secure suggestions...")
    with tqdm(total=num_suggestions, desc="Suggestions Generated") as pbar:
        while len(suggestions) < num_suggestions:
            enhanced = enhance_password(password)
            is_safe, distance = is_password_safe_with_levenshtein(enhanced, compromised_passwords, threshold=0.6)
            if is_safe:
                suggestions.append(enhanced)
                pbar.update(1)
    return suggestions

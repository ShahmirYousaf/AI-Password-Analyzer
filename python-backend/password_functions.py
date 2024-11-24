# Importing necessary libraries
import random
import string
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import fasttext
import torch
import Levenshtein
import re

# Load RoBERTa model and tokenizer
roberta_model = RobertaForSequenceClassification.from_pretrained("./password_strength_roberta")
roberta_tokenizer = RobertaTokenizer.from_pretrained("./password_strength_roberta")

# Load FastText model
fasttext_model_path = "fasttext_rockyou.bin"
fasttext_model = fasttext.load_model(fasttext_model_path)

# Load precomputed embeddings and compromised passwords
compromised_embeddings = np.load("rockyou_embeddings.npy", allow_pickle=True)
with open("rockyou.txt", "r", encoding="latin1") as f:
    compromised_passwords = [line.strip() for line in f]

# Function to classify password strength using RoBERTa
def classify_password(password):
    inputs = roberta_tokenizer(password, return_tensors="pt", truncation=True, padding=True, max_length=32)
    outputs = roberta_model(**inputs)
    predicted_class = torch.argmax(outputs.logits, dim=1).item()
    labels = ["Weak", "Moderate", "Strong"]
    return labels[predicted_class]

# Function to check password similarity
def check_password_similarity(input_password, top_n=100):
    input_embedding = fasttext_model.get_sentence_vector(input_password)
    similarities = cosine_similarity([input_embedding], compromised_embeddings)[0]
    top_indices = similarities.argsort()[-top_n:][::-1]
    shortlisted_passwords = [compromised_passwords[i] for i in top_indices]

    best_password = None
    lowest_distance = float('inf')
    for candidate in tqdm(shortlisted_passwords, desc="Processing candidates"):
        distance = Levenshtein.distance(input_password, candidate) / max(len(input_password), len(candidate))
        if distance < lowest_distance:
            lowest_distance = distance
            best_password = candidate

    similarity_percentage = max(similarities) * 100
    status = "Password Compromised" if lowest_distance < 0.7 else "Password Safe"
    return best_password, similarity_percentage, status, (1 - lowest_distance) * 100

# Function for rule-based feedback on password
def rule_based_feedback(password, status):
    if status == "Password Safe":
        return "Your password is strong and safe to use. No changes required!"

    feedback = []
    if len(password) < 8:
        feedback.append("Your password is too short. Use at least 8 characters.")
    if not any(char.isupper() for char in password):
        feedback.append("Add at least one uppercase letter.")
    if not any(char.islower() for char in password):
        feedback.append("Add at least one lowercase letter.")
    if not any(char.isdigit() for char in password):
        feedback.append("Include at least one number.")
    if not any(char in "!@#$%^&*()_+[]{}|;:,.<>?/`~" for char in password):
        feedback.append("Add at least one special character (e.g., !, @, #, $).")
    if re.search(r"(password|1234|abcd|qwerty|admin)", password, re.IGNORECASE):
        feedback.append("Avoid using common patterns or dictionary words.")
    if re.search(r"(.)\1{2,}", password):
        feedback.append("Avoid repetitive characters.")

    return " ".join(feedback)

# Function to enhance password
def enhance_password(password):
    special_characters = "!@#$%^&*"
    enhanced_password = list(password)
    for i in range(len(enhanced_password)):
        if random.random() < 0.1:
            enhanced_password[i] = random.choice(special_characters)
        elif random.random() < 0.3:
            enhanced_password[i] = enhanced_password[i].swapcase()

    enhanced_password.insert(0, random.choice(special_characters))
    enhanced_password.append(random.choice(special_characters))
    enhanced_password.append(str(random.randint(10, 99)))
    while len(enhanced_password) < 8:
        enhanced_password.append(random.choice(string.ascii_letters).upper())

    return "".join(enhanced_password)

# Function to check if password is safe
def is_password_safe_with_levenshtein(password, threshold=0.7):
    for compromised_password in compromised_passwords:
        distance = Levenshtein.distance(password, compromised_password) / max(len(password), len(compromised_password))
        if distance < threshold:
            return False, distance * 100
    return True, None

# Function to generate secure password suggestions
def generate_secure_suggestions(password, num_suggestions=3):
    suggestions = []
    with tqdm(total=num_suggestions, desc="Suggestions Generated") as pbar:
        while len(suggestions) < num_suggestions:
            enhanced = enhance_password(password)
            is_safe, distance = is_password_safe_with_levenshtein(enhanced, threshold=0.6)
            if is_safe:
                suggestions.append(enhanced)
                pbar.update(1)
    return suggestions

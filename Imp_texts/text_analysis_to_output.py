import os
import re
import string
import pandas as pd
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter

# ========== Load Stop Words ==========
def load_stopwords(folder_path):
    stop_words = set()
    for filename in os.listdir(folder_path):
        with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
            for line in file:
                word = line.strip().lower()
                if word:
                    stop_words.add(word)
    return stop_words

# ========== Load Master Dictionary ==========
def load_sentiment_words(dictionary_path):
    with open(dictionary_path, 'r') as file:
        return set(word.strip().lower() for word in file if word.strip())

# ========== Utility Functions ==========
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[\r\n]+", " ", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text

def count_syllables(word):
    word = word.lower()
    word = re.sub(r'(es|ed)$', '', word)
    return len(re.findall(r'[aeiouy]', word))

def is_complex(word):
    return count_syllables(word) > 2

def count_personal_pronouns(text):
    pronouns = re.findall(r'\b(I|we|my|ours|us)\b', text, re.I)
    return len(pronouns)

# ========== Analysis Function ==========
def analyze_text(text, stop_words, pos_words, neg_words):
    clean = clean_text(text)
    words = word_tokenize(clean)
    words_cleaned = [w for w in words if w not in stop_words and w not in string.punctuation]

    # Sentiment Scores
    pos_score = sum(1 for word in words_cleaned if word in pos_words)
    neg_score = sum(1 for word in words_cleaned if word in neg_words)
    polarity_score = (pos_score - neg_score) / ((pos_score + neg_score) + 1e-6)
    subjectivity_score = (pos_score + neg_score) / (len(words_cleaned) + 1e-6)

    # Readability Metrics
    sentences = sent_tokenize(text)
    total_words = len(words_cleaned)
    total_sentences = len(sentences) if len(sentences) > 0 else 1
    avg_sentence_length = total_words / total_sentences
    complex_words = [w for w in words_cleaned if is_complex(w)]
    percent_complex = len(complex_words) / total_words if total_words > 0 else 0
    fog_index = 0.4 * (avg_sentence_length + percent_complex * 100)
    avg_words_per_sentence = avg_sentence_length
    complex_word_count = len(complex_words)
    syllable_per_word = sum(count_syllables(w) for w in words_cleaned) / total_words if total_words > 0 else 0
    personal_pronouns = count_personal_pronouns(text)
    avg_word_length = sum(len(w) for w in words_cleaned) / total_words if total_words > 0 else 0

    return [
        pos_score, neg_score, polarity_score, subjectivity_score,
        avg_sentence_length, percent_complex * 100, fog_index,
        avg_words_per_sentence, complex_word_count, total_words,
        syllable_per_word, personal_pronouns, avg_word_length
    ]

# ========== Main Execution ==========
if __name__ == "__main__":
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')

    # Paths
    base_dir = os.getcwd()
    articles_dir = os.path.join(base_dir, "extracted_articles_from_input_excel_2")
    stopwords_dir = os.path.join(base_dir, "Stop Words")
    pos_dict_path = os.path.join(base_dir, "MasterDictionary", "positive-words.txt")
    neg_dict_path = os.path.join(base_dir, "MasterDictionary", "negative-words.txt")
    output_txt_path = os.path.join(base_dir, "output", "output.txt")
    output_xlsx_path = os.path.join(base_dir, "output", "output.xlsx")

    os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)

    stop_words = load_stopwords(stopwords_dir)
    pos_words = load_sentiment_words(pos_dict_path)
    neg_words = load_sentiment_words(neg_dict_path)

    results = []

    for file in os.listdir(articles_dir):
        if file.endswith(".txt"):
            url_id = file.replace(".txt", "")
            with open(os.path.join(articles_dir, file), "r", encoding="utf-8") as f:
                text = f.read()

            metrics = analyze_text(text, stop_words, pos_words, neg_words)
            results.append([url_id, ""] + metrics)  # leave URL blank for now

    # Save to Excel
    columns = [
        "URL_ID", "URL", "POSITIVE SCORE", "NEGATIVE SCORE", "POLARITY SCORE", "SUBJECTIVITY SCORE",
        "AVG SENTENCE LENGTH", "PERCENTAGE OF COMPLEX WORDS", "FOG INDEX",
        "AVG NUMBER OF WORDS PER SENTENCE", "COMPLEX WORD COUNT", "WORD COUNT",
        "SYLLABLE PER WORD", "PERSONAL PRONOUNS", "AVG WORD LENGTH"
    ]
    df = pd.DataFrame(results, columns=columns)
    df.to_excel(output_xlsx_path, index=False)

    # Save to text
    with open(output_txt_path, "w", encoding="utf-8") as f:
        for row in results:
            f.write(", ".join(map(str, row)) + "\n")

    print("Text analysis completed and results saved to output.txt and output.xlsx")

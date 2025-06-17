import os
import re
import nltk
import string
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter
import pandas as pd
import chardet

# Download necessary NLTK resources
nltk.download('punkt_tab')
nltk.download('stopwords')

# Paths
BASE_DIR = "E:/BLACKCOFFER INTERNSHIP TASKS/CODING_PART/TEXT_ANALYSIS_PART"
ARTICLE_DIR = os.path.join(BASE_DIR, "extracted_articles_from_input_excel_2")
STOPWORDS_DIR = os.path.join(BASE_DIR, "Stop Words")
DICTIONARY_DIR = os.path.join(BASE_DIR, "MasterDictionary")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def load_stopwords():
    stopwords_set = set()
    # Add NLTK's stopwords
    stopwords_set.update(word.upper() for word in stopwords.words('english'))
    
    # Add custom stopwords
    for file in os.listdir(STOPWORDS_DIR):
        file_path = os.path.join(STOPWORDS_DIR, file)
        try:
            encoding = detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                for line in f:
                    word = line.strip().split('|')[0].strip().upper()
                    if word:
                        stopwords_set.add(word)
        except Exception as e:
            print(f"Error loading stopwords from {file_path}: {e}")
    return stopwords_set

# Load Positive and Negative Words
def load_sentiment_words():
    pos_words = set()
    neg_words = set()
    
    try:
        with open(os.path.join(DICTIONARY_DIR, "positive-words.txt"), 'r', encoding='latin-1') as f:
            pos_words = set([line.strip().upper() for line in f if line.strip() and not line.startswith(';')])
        
        with open(os.path.join(DICTIONARY_DIR, "negative-words.txt"), 'r', encoding='latin-1') as f:
            neg_words = set([line.strip().upper() for line in f if line.strip() and not line.startswith(';')])
    except Exception as e:
        print(f"Error loading sentiment dictionaries: {e}")
        
    return pos_words, neg_words

# Clean text
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

# Syllable counter
def count_syllables(word):
    word = word.lower()
    vowels = "aeiouy"
    syllable_count = 0
    if len(word) > 0 and word[0] in vowels:
        syllable_count += 1
    for i in range(1, len(word)):
        if word[i] in vowels and word[i - 1] not in vowels:
            syllable_count += 1
    if word.endswith("es") or word.endswith("ed"):
        syllable_count -= 1
    return max(1, syllable_count)

# Personal pronoun finder
def count_personal_pronouns(text):
    pronouns = re.findall(r'\b(I|we|my|ours|us)\b', text, re.I)
    filtered = [p for p in pronouns if p.lower() != "us"]
    return len(filtered)

# Complex word checker
def is_complex(word):
    return count_syllables(word) > 2

# Main analysis function
def analyze_text_file(filepath, stop_words, pos_dict, neg_dict):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            text = file.read()

        cleaned = clean_text(text)
        
        # Use simple tokenization if NLTK tokenization fails
        try:
            words = word_tokenize(cleaned)
            sentences = sent_tokenize(cleaned)
        except LookupError:
            print("NLTK tokenization failed, using simple tokenization")
            words = cleaned.split()
            sentences = re.split(r'[.!?]+', cleaned)
        
        # Filter out empty sentences
        sentences = [s for s in sentences if s.strip()]
        
        # Uppercase all words to match dictionary
        filtered_words = [w.upper() for w in words if w.upper() not in stop_words and w.isalpha()]
        
        # Avoid division by zero
        total_words = max(1, len(filtered_words))
        num_sentences = max(1, len(sentences))
        
        # Sentiment
        pos_score = sum(1 for w in filtered_words if w in pos_dict)
        neg_score = sum(1 for w in filtered_words if w in neg_dict)
        polarity_score = (pos_score - neg_score) / ((pos_score + neg_score) + 0.000001)
        subjectivity_score = (pos_score + neg_score) / total_words

        # Readability
        complex_words = [w for w in filtered_words if is_complex(w)]
        percent_complex_words = len(complex_words) / total_words
        avg_sentence_length = total_words / num_sentences
        fog_index = 0.4 * (avg_sentence_length + percent_complex_words)

        # Other metrics
        avg_words_per_sentence = avg_sentence_length
        complex_word_count = len(complex_words)
        word_count = total_words
        syllable_per_word = sum(count_syllables(w) for w in filtered_words) / total_words
        personal_pronouns = count_personal_pronouns(text)
        avg_word_length = sum(len(w) for w in filtered_words) / total_words

        return {
            'POSITIVE SCORE': pos_score,
            'NEGATIVE SCORE': neg_score,
            'POLARITY SCORE': polarity_score,
            'SUBJECTIVITY SCORE': subjectivity_score,
            'AVG SENTENCE LENGTH': avg_sentence_length,
            'PERCENTAGE OF COMPLEX WORDS': percent_complex_words,
            'FOG INDEX': fog_index,
            'AVG NUMBER OF WORDS PER SENTENCE': avg_words_per_sentence,
            'COMPLEX WORD COUNT': complex_word_count,
            'WORD COUNT': word_count,
            'SYLLABLE PER WORD': syllable_per_word,
            'PERSONAL PRONOUNS': personal_pronouns,
            'AVG WORD LENGTH': avg_word_length
        }
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        # Return default values
        return {
            'POSITIVE SCORE': 0, 'NEGATIVE SCORE': 0, 'POLARITY SCORE': 0,
            'SUBJECTIVITY SCORE': 0, 'AVG SENTENCE LENGTH': 0, 'PERCENTAGE OF COMPLEX WORDS': 0,
            'FOG INDEX': 0, 'AVG NUMBER OF WORDS PER SENTENCE': 0, 'COMPLEX WORD COUNT': 0,
            'WORD COUNT': 0, 'SYLLABLE PER WORD': 0, 'PERSONAL PRONOUNS': 0, 'AVG WORD LENGTH': 0
        }

# Run analysis for all files
def run_analysis():
    try:
        print("Loading stopwords...")
        stop_words = load_stopwords()
        print("Loading sentiment dictionaries...")
        pos_dict, neg_dict = load_sentiment_words()
        
        results = []
        print(f"Analyzing files in {ARTICLE_DIR}...")
        files = [f for f in os.listdir(ARTICLE_DIR) if f.endswith(".txt")]
        
        if not files:
            print(f"No text files found in {ARTICLE_DIR}")
            return
            
        for i, filename in enumerate(files):
            file_path = os.path.join(ARTICLE_DIR, filename)
            print(f"Processing {i+1}/{len(files)}: {filename}")
            result = analyze_text_file(file_path, stop_words, pos_dict, neg_dict)
            result['FILENAME'] = filename
            results.append(result)
        
        df = pd.DataFrame(results)
        df = df[['FILENAME'] + [col for col in df.columns if col != 'FILENAME']]
        output_path = os.path.join(OUTPUT_DIR, 'output.xlsx')
        df.to_excel(output_path, index=False)
        print(f"Analysis completed. Results saved to: {output_path}")
    except Exception as e:
        print(f"Error in analysis: {e}")

if __name__ == "__main__":
    run_analysis()
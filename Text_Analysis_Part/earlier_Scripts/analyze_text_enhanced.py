import os
import re
import nltk
import string
from collections import Counter
import pandas as pd
import chardet
import sys

# Set up a dedicated NLTK data directory in your project folder
NLTK_DATA_DIR = os.path.join("E:/BLACKCOFFER INTERNSHIP TASKS/CODING_PART/TEXT_ANALYSIS_PART", "nltk_data")
os.makedirs(NLTK_DATA_DIR, exist_ok=True)
nltk.data.path.append(NLTK_DATA_DIR)

# Download NLTK resources with explicit path
print("Downloading NLTK resources...")
nltk.download('punkt_tab', download_dir=NLTK_DATA_DIR, quiet=False)
nltk.download('stopwords', download_dir=NLTK_DATA_DIR, quiet=False)

# Import after download to ensure resources are loaded
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Paths
BASE_DIR = "E:/BLACKCOFFER INTERNSHIP TASKS/CODING_PART/TEXT_ANALYSIS_PART"
ARTICLE_DIR = os.path.join(BASE_DIR, "extracted_articles_from_input_excel_2")
STOPWORDS_DIR = os.path.join(BASE_DIR, "Stop Words")
DICTIONARY_DIR = os.path.join(BASE_DIR, "MasterDictionary")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def detect_encoding(file_path):
    """Detect file encoding"""
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding']
    except Exception as e:
        print(f"Error detecting encoding for {file_path}: {e}")
        return 'utf-8'  # Default to UTF-8

def load_stopwords():
    """Load all stopwords from files and NLTK"""
    print("Loading stopwords...")
    stopwords_set = set()
    
    # Add NLTK's stopwords
    try:
        stopwords_set.update(word.upper() for word in stopwords.words('english'))
    except Exception as e:
        print(f"Warning: Could not load NLTK stopwords: {e}")
    
    # Add custom stopwords from files
    for file in os.listdir(STOPWORDS_DIR):
        file_path = os.path.join(STOPWORDS_DIR, file)
        try:
            encoding = detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                for line in f:
                    if '|' in line:
                        word = line.strip().split('|')[0].strip().upper()
                    else:
                        word = line.strip().upper()
                    if word:
                        stopwords_set.add(word)
        except Exception as e:
            print(f"Warning: Error loading stopwords from {file_path}: {e}")
    
    print(f"Loaded {len(stopwords_set)} stopwords")
    return stopwords_set

def load_sentiment_words():
    """Load positive and negative sentiment words"""
    print("Loading sentiment dictionaries...")
    pos_words = set()
    neg_words = set()
    
    try:
        pos_path = os.path.join(DICTIONARY_DIR, "positive-words.txt")
        encoding = detect_encoding(pos_path)
        with open(pos_path, 'r', encoding=encoding, errors='ignore') as f:
            pos_words = set([line.strip().upper() for line in f if line.strip() and not line.startswith(';')])
        
        neg_path = os.path.join(DICTIONARY_DIR, "negative-words.txt")
        encoding = detect_encoding(neg_path)
        with open(neg_path, 'r', encoding=encoding, errors='ignore') as f:
            neg_words = set([line.strip().upper() for line in f if line.strip() and not line.startswith(';')])
        
        print(f"Loaded {len(pos_words)} positive words and {len(neg_words)} negative words")
    except Exception as e:
        print(f"Error loading sentiment dictionaries: {e}")
        
    return pos_words, neg_words

# Custom tokenizers to use as fallbacks
def custom_sentence_tokenize(text):
    """Custom sentence tokenizer that doesn't rely on NLTK's punkt"""
    # Split on sentence endings followed by space or newline
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def custom_word_tokenize(text):
    """Custom word tokenizer that doesn't rely on NLTK"""
    # Split on whitespace and remove punctuation
    words = re.findall(r'\b\w+\b', text.lower())
    return [w for w in words if w]

def clean_text(text):
    """Clean text by removing extra whitespace and punctuation"""
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.strip()

def count_syllables(word):
    """Count syllables in a word"""
    word = word.lower()
    # Exception for words ending with 'es' or 'ed'
    if word.endswith('es') or word.endswith('ed'):
        word = word[:-2]
    
    # Count vowel groups
    vowels = "aeiouy"
    # Remove consecutive vowels (count as one syllable)
    word = re.sub(r'[aeiouy]+', 'a', word)
    # Count vowels
    count = sum(1 for char in word if char in vowels)
    
    # Every word has at least one syllable
    return max(1, count)

def is_complex(word):
    """Check if a word is complex (more than 2 syllables)"""
    return count_syllables(word) > 2

def count_personal_pronouns(text):
    """Count personal pronouns in text"""
    # Find pronouns while avoiding 'US' as country name
    pronouns = re.findall(r'\b(I|we|my|ours|us)\b', text, re.I)
    # Filter out 'US' when it's likely the country
    filtered = [p for p in pronouns if not (p.lower() == 'us' and p.isupper())]
    return len(filtered)

def analyze_text_file(filepath, stop_words, pos_dict, neg_dict):
    """Analyze a text file and extract metrics"""
    try:
        # Read file with appropriate encoding
        try:
            encoding = detect_encoding(filepath)
            with open(filepath, 'r', encoding=encoding, errors='ignore') as file:
                text = file.read()
        except UnicodeDecodeError:
            # Fallback to utf-8
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
        
        # Clean text
        cleaned = clean_text(text)
        
        # Try NLTK tokenization with fallback to custom tokenizers
        try:
            # Try NLTK tokenization
            from nltk.tokenize import sent_tokenize
            sentences = sent_tokenize(cleaned)
            words = word_tokenize(cleaned)
        except Exception as e:
            print(f"NLTK tokenization failed ({e}), using custom tokenization")
            sentences = custom_sentence_tokenize(cleaned)
            words = custom_word_tokenize(cleaned)
        
        # Ensure we have valid sentences and words
        sentences = [s for s in sentences if s.strip()]
        if not sentences:
            sentences = [cleaned]  # Use whole text as one sentence if no sentences found
        
        # Filter words using stopwords
        filtered_words = [w.upper() for w in words if w.upper() not in stop_words and w.isalpha()]
        
        # Ensure we have at least some words to analyze
        if not filtered_words and words:
            filtered_words = [w.upper() for w in words if w.isalpha()]
        
        # Avoid division by zero
        total_words = max(1, len(filtered_words))
        num_sentences = max(1, len(sentences))
        
        # Calculate sentiment scores
        pos_score = sum(1 for w in filtered_words if w in pos_dict)
        neg_score = sum(1 for w in filtered_words if w in neg_dict)
        
        # Calculate polarity and subjectivity
        polarity_denominator = (pos_score + neg_score) + 0.000001  # Avoid division by zero
        polarity_score = (pos_score - neg_score) / polarity_denominator
        subjectivity_score = (pos_score + neg_score) / (total_words + 0.000001)

        # Calculate readability metrics
        complex_words = [w for w in filtered_words if is_complex(w)]
        percent_complex_words = len(complex_words) / total_words
        avg_sentence_length = total_words / num_sentences
        fog_index = 0.4 * (avg_sentence_length + percent_complex_words)

        # Calculate other metrics
        syllable_count = sum(count_syllables(w) for w in filtered_words)
        syllable_per_word = syllable_count / total_words
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
            'AVG NUMBER OF WORDS PER SENTENCE': avg_sentence_length,  # Same as AVG SENTENCE LENGTH
            'COMPLEX WORD COUNT': len(complex_words),
            'WORD COUNT': total_words,
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

def run_analysis():
    """Run the analysis on all text files and save results"""
    try:
        # Load resources
        stop_words = load_stopwords()
        pos_dict, neg_dict = load_sentiment_words()
        
        # Get all text files
        files = [f for f in os.listdir(ARTICLE_DIR) if f.endswith(".txt")]
        if not files:
            print(f"No text files found in {ARTICLE_DIR}")
            return
        
        print(f"Found {len(files)} text files to analyze")
        
        # Process each file
        results = []
        for i, filename in enumerate(files):
            file_path = os.path.join(ARTICLE_DIR, filename)
            print(f"Processing {i+1}/{len(files)}: {filename}")
            
            # Analyze file
            result = analyze_text_file(file_path, stop_words, pos_dict, neg_dict)
            result['FILENAME'] = filename
            results.append(result)
            
            # Print progress every 10 files
            if (i + 1) % 10 == 0:
                print(f"Processed {i+1}/{len(files)} files")
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(results)
        columns = ['FILENAME', 'POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE', 
                   'SUBJECTIVITY SCORE', 'AVG SENTENCE LENGTH', 'PERCENTAGE OF COMPLEX WORDS',
                   'FOG INDEX', 'AVG NUMBER OF WORDS PER SENTENCE', 'COMPLEX WORD COUNT',
                   'WORD COUNT', 'SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 'AVG WORD LENGTH']
        
        # Ensure all columns exist (add missing ones with default values)
        for col in columns:
            if col not in df.columns:
                df[col] = 0
        
        # Reorder columns
        df = df[columns]
        
        # Save to Excel
        output_path = os.path.join(OUTPUT_DIR, 'output.xlsx')
        df.to_excel(output_path, index=False)
        print(f"Analysis completed. Results saved to: {output_path}")
    except Exception as e:
        print(f"Error in analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print(f"NLTK version: {nltk.__version__}")
    print(f"Starting text analysis...")
    run_analysis()
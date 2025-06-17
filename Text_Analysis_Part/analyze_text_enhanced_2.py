#  importing all the necessary libraries for the text processing part
import os
import re
import nltk
import string
from collections import Counter
import pandas as pd
import chardet
import sys


#  Set up a dedicated NLTK data directory in your project folder as I was having problem with this in my C directory
NLTK_DATA_DIR = os.path.join("E:/BLACKCOFFER INTERNSHIP TASKS/CODING_PART/TEXT_ANALYSIS_PART", "nltk_data")
os.makedirs(NLTK_DATA_DIR, exist_ok=True)
nltk.data.path.append(NLTK_DATA_DIR)

#  Download NLTK resources with explicit path in the working directory, this will be run once only we change it later
print("Downloading NLTK resources...")
nltk.download('punkt_tab', download_dir=NLTK_DATA_DIR, quiet=False)
nltk.download('stopwords', download_dir=NLTK_DATA_DIR, quiet=False)

#  Import after download to ensure resources are loaded, as a error callable
try:
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
except exception as e:
    print(f"No library found {e}")

#  Paths
#  BASE_DIR = the current working directory"
BASE_DIR = os.getcwd()
ARTICLE_DIR = os.path.join(BASE_DIR, "extracted_articles_from_input_excel_2")
STOPWORDS_DIR = os.path.join(BASE_DIR, "Stop Words")
DICTIONARY_DIR = os.path.join(BASE_DIR, "MasterDictionary")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

#  Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def detect_encoding(file_path):
    #  Detect file encoding
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding']
    except Exception as e:
        print(f"Error detecting encoding for {file_path}: {e}")
        return 'utf-8'  #  Default to UTF-8

def load_stopwords():
    #  Load all stopwords from files and NLTK
    print("Loading stopwords...")
    stopwords_set = set()
    
    #  Add NLTK's stopwords
    try:
        stopwords_set.update(word.upper() for word in stopwords.words('english'))
    except Exception as e:
        print(f"Warning: Could not load NLTK stopwords: {e}")
    
    #  Add custom stopwords from files
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
    # Loading the positive and negative sentiment words # 
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

#  Custom tokenizers to use as fallbacks if the NLTK one does not works ( FACING SOME ISSUUE WITH THE DEFAULT ONE)
def custom_sentence_tokenize(text):
    # Custom sentence tokenizer that doesn't rely on NLTK's punkt # 
    #  Split on sentence endings followed by space or newline
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def custom_word_tokenize(text):
    # Custom word tokenizer that doesn't rely on NLTK# 
    #  Split on whitespace and remove punctuation
    words = re.findall(r'\b\w+\b', text.lower())
    return [w for w in words if w]

def clean_text(text):
    # Clean text by removing extra whitespace and punctuation# 
    #  Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    #  Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.strip()

def count_syllables(word):
    # Counting the syllables in a word# 
    word = word.lower()
    #  Exception for words ending with 'es' or 'ed'
    if word.endswith('es') or word.endswith('ed'):
        word = word[:-2]
    
    #  Count vowel groups
    vowels = "aeiouy"
    #  Remove consecutive vowels (count as one syllable)
    word = re.sub(r'[aeiouy]+', 'a', word)
    #  Count vowels
    count = sum(1 for char in word if char in vowels)
    
    #  Every word has at least one syllable
    return max(1, count)

def is_complex(word):
    # Check if a word is complex (more than 2 syllables)"""
    return count_syllables(word) > 2

def count_personal_pronouns(text):
    # Count personal pronouns in text# 
    #  Find pronouns while avoiding 'US' as country name
    pronouns = re.findall(r'\b(I|we|my|ours|us)\b', text, re.I)
    #  Filter out 'US' when it's likely the country
    filtered = [p for p in pronouns if not (p.lower() == 'us' and p.isupper())]
    return len(filtered)

def analyze_text_file(filepath, stop_words, pos_dict, neg_dict):
    # Analyze a text file and extract metrics# 
    try:
        #  Read file with appropriate encoding
        try:
            encoding = detect_encoding(filepath)
            with open(filepath, 'r', encoding=encoding, errors='ignore') as file:
                text = file.read()
        except UnicodeDecodeError:
            #  Fallback to utf-8
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
        
        #  Clean text
        cleaned = clean_text(text)
        
        #  Try NLTK tokenization with fallback to custom tokenizers
        try:
            #  Try NLTK tokenization
            from nltk.tokenize import sent_tokenize
            sentences = sent_tokenize(cleaned)
            words = word_tokenize(cleaned)
            
        except Exception as e:
            # Now trying with the fallback one which will eventually work
            print(f"NLTK tokenization failed ({e}), using custom tokenization")
            sentences = custom_sentence_tokenize(cleaned)
            words = custom_word_tokenize(cleaned)
        
        #  Ensuring we have valid sentences and words
        sentences = [s for s in sentences if s.strip()]
        if not sentences:
            sentences = [cleaned]  #  Use whole text as one sentence if no sentences found
        
        #  Filtering words using stopwords
        filtered_words = [w.upper() for w in words if w.upper() not in stop_words and w.isalpha()]
        
        #  Ensuring we have at least some words to analyze
        if not filtered_words and words:
            filtered_words = [w.upper() for w in words if w.isalpha()]
        
        #  division by zero avoidance -> will give 1 if there are 0
        total_words = max(1, len(filtered_words))
        num_sentences = max(1, len(sentences))
        
        #  Calculating the sentiment scores
        # the positive score -> +1 for each +ve word
        pos_score = sum(1 for w in filtered_words if w in pos_dict)
        # the negative score -> -1 for each -ve word 
        neg_score = sum(1 for w in filtered_words if w in neg_dict)
        
        #  Calculate polarity and subjectivity
        polarity_denominator = (pos_score + neg_score) + 0.000001  #  Avoiding division by zero , hence adding 0.000001
        polarity_score = (pos_score - neg_score) / polarity_denominator
        subjectivity_score = (pos_score + neg_score) / (total_words + 0.000001)

        #  Calculate readability metrics
        complex_words = [w for w in filtered_words if is_complex(w)]
        percent_complex_words = len(complex_words) / total_words
        avg_sentence_length = total_words / num_sentences
        fog_index = 0.4 * (avg_sentence_length + percent_complex_words)

        #  Calculate other metrics
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
            'AVG NUMBER OF WORDS PER SENTENCE': avg_sentence_length,  #  Same as AVG SENTENCE LENGTH
            'COMPLEX WORD COUNT': len(complex_words),
            'WORD COUNT': total_words,
            'SYLLABLE PER WORD': syllable_per_word,
            'PERSONAL PRONOUNS': personal_pronouns,
            'AVG WORD LENGTH': avg_word_length
        }
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        #  Returning default values if any error happens
        return {
            'POSITIVE SCORE': 0, 'NEGATIVE SCORE': 0, 'POLARITY SCORE': 0,
            'SUBJECTIVITY SCORE': 0, 'AVG SENTENCE LENGTH': 0, 'PERCENTAGE OF COMPLEX WORDS': 0,
            'FOG INDEX': 0, 'AVG NUMBER OF WORDS PER SENTENCE': 0, 'COMPLEX WORD COUNT': 0,
            'WORD COUNT': 0, 'SYLLABLE PER WORD': 0, 'PERSONAL PRONOUNS': 0, 'AVG WORD LENGTH': 0
        }

def run_analysis():
    # Main run the analysis function on all text files and update an existing output Excel file # 
    try:
        #  Loading resources
        stop_words = load_stopwords()
        pos_dict, neg_dict = load_sentiment_words()
        
        #  Load the existing Excel file
        output_excel_path = os.path.join(OUTPUT_DIR, 'output.xlsx')
        try:
            existing_df = pd.read_excel(output_excel_path)
            print(f"Loaded existing Excel file with {len(existing_df)} rows")
        except Exception as e:
            print(f"Error loading existing Excel file: {e}")
            print("Please ensure output.xlsx exists in the output directory")
            return
        
        #  Get all text files
        files = [f for f in os.listdir(ARTICLE_DIR) if f.endswith(".txt")]
        if not files:
            print(f"No text files found in {ARTICLE_DIR}")
            return
        
        print(f"Found {len(files)} text files to analyze")
        
        #  Processing each file
        files_processed = 0
        for i, filename in enumerate(files):
            file_path = os.path.join(ARTICLE_DIR, filename)
            print(f"Processing {i+1}/{len(files)}: {filename}")
            
            #  Extractinf the URL_ID from filename (assuming filename format matches URL_ID in Excel)
            url_id = filename.replace('.txt', '')
            
            #  Checking if the filename exists in the Excel file
            if 'FILENAME' in existing_df.columns and filename in existing_df['FILENAME'].values:
                match_column = 'FILENAME'
                match_value = filename
            #  Otherwise checking if URL_ID exists
            elif 'URL_ID' in existing_df.columns and url_id in existing_df['URL_ID'].values:
                match_column = 'URL_ID'
                match_value = url_id
            else:
                print(f"Warning: Neither {filename} nor {url_id} found in the output Excel file. Skipping...")
                continue
            
            #  Then we analyze the file
            result = analyze_text_file(file_path, stop_words, pos_dict, neg_dict)
            
            #  We update the corresponding row in the DataFrame
            row_idx = existing_df.index[existing_df[match_column] == match_value].tolist()
            if row_idx:
                for key, value in result.items():
                    if key in existing_df.columns:
                        existing_df.at[row_idx[0], key] = value
                files_processed += 1
            
            #  For better error handling and log output, I am printing every progress every 10 files which are processed
            if (i + 1) % 10 == 0:
                print(f"Processed {i+1}/{len(files)} files")
        
        #  Save updated DataFrame back to Excel
        existing_df.to_excel(output_excel_path, index=False)
        print(f"Analysis completed. Updated {files_processed} entries in: {output_excel_path}")
    except Exception as e:
        print(f"Error in analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Earlier I was having issues with the nltk versiono hence I was printing the version number of both nltk and the python
    # print(f"Python version: {sys.version}")
    # print(f"NLTK version: {nltk.__version__}")
    print(f"Starting text analysis...")
    run_analysis()
# How I achieved what I have done!

# Problem Statement
* ** Given a list of web page URLs in an Excel file, the task is to:

- Automatically extract the full textual content from each web page.

- Analyze the extracted text using various Natural Language Processing (NLP) techniques including sentiment analysis, readability, and lexical metrics.

- Generate a structured Excel output that summarizes the computed metrics for each document in a clean tabular format.

# Key Challenges:
- Many URLs are dynamically rendered, requiring a browser-based scraping approach (static parsing fails).

- Need for automated, large-scale processing (147+ pages) with logging, retry handling, and fallback mechanisms.

- Requirement to perform custom NLP-based analysis, based on predefined formulas and dictionary-based sentiment scoring.

- Consistency in file structure and data flow from extraction → processing → output.

## Solution Overview

This repository contains the implementation of a two-part task:

1. **Extraction** of content from a list of web URLs.
2. **Text Analysis** on the extracted content using basic NLP techniques.

The task is organized into two main directories: `Extraction_Part` and `Text_Analysis_Part`, each with their own script files, logs, and supporting resources.

---

## 1. Approach

### Step-by-step Breakdown

#### A) **Extraction Part**

* **Initial Exploration**: Started by checking the input Excel file and manually exploring some URLs to understand how content is structured and how to access it.

* **Tool Selection**: Initially tried using `BeautifulSoup`, but due to JS-rendered content on some URLs, switched to `Selenium`.

* **Final Script**: Created the main script - `enhanced_scraping_using_input_url.py` which:

  * Uses Selenium with Edge WebDriver.
  * Extracts content via specific XPaths.
  * Implements a logging mechanism to track progress, retries, and failures.

* **Directory Structure**

  ```
  Extraction_Part/
  ├── enhanced_scraping_using_input_url.py
  ├── earlier Scripts/
  ├── edge_driver/
  ├── input/
  ├── extracted_articles_from_input_excel_2/
  └── scraping_logs/
  ```

* **Behavior**

  * Input URLs are read from `input/Input.xlsx`.
  * Extracted articles are saved using their URL\_IDs into `extracted_articles_from_input_excel_2`.
  * All logs related to scraping are stored in the `scraping_logs` folder.
  * The script retries on failures (2 more attempts before skipping) to avoid loss due to unstable connections.

#### B) **Text Analysis Part**

* **Function Implementation**: After collecting content files, implemented a script for analyzing text documents based on an external document specifying formulas.

* **NLP Issues & Fixes**:

  * Faced path and tokenizer issues with NLTK.
  * Downloaded `nltk_data` manually inside the working directory to resolve path issues.
  * Designed a custom tokenizer temporarily, then fixed the issue with `nltk.download('punkt_tab')`.

* **Final Script**: `analyze_text_enhanced_2.py` handles:

  * Tokenization
  * Stopwords removal
  * Positive/Negative word count from the provided MasterDictionary
  * Other calculated metrics

* **Directory Structure**

  ```
  Text_Analysis_Part/
  ├── analyze_text_enhanced_2.py
  ├── text_analysis_doc.txt
  ├── earlier_Scripts/
  ├── extracted_articles_from_input_excel_2/
  ├── MasterDictionary/
  ├── nltk_data/
  └── output/
  ```

* **Behavior**

  * Processes all `.txt` files from `extracted_articles_from_input_excel_2`.
  * Produces `output.xlsx` containing computed text analysis metrics.

---

## 2. How to Run

### Step 1: Extraction

```bash
cd Extraction_Part
python enhanced_scraping_using_input_url.py
```

* Make sure `input/Input.xlsx` exists.
* Scraped contents will appear in `extracted_articles_from_input_excel_2/`.
* Logs will be saved in `scraping_logs/`.

### Step 2: Text Analysis

```bash
cd Text_Analysis_Part
python analyze_text_enhanced_2.py
```

* Output will be saved as `output.xlsx` in the same directory.
* Logs and console output will show progress for each document.

---

## 3. Dependencies

### For Extraction Part

Install via pip:

```bash
pip install selenium pandas
```

You’ll also need the [Microsoft Edge WebDriver](https://developer.microsoft.com/en-in/microsoft-edge/tools/webdriver?form=MA13LH#downloads). Place `msedgedriver.exe` inside the `edge_driver/` directory.

Imports used:

```python
import os
import pandas as pd
import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
```

### For Text Analysis Part

Install via pip:

```bash
pip install nltk pandas chardet
```

NLTK Resources:

* `punkt_tab`
* `stopwords`
* MasterDictionary (positive and negative words)

Imports used:

```python
import os
import re
import nltk
import string
from collections import Counter
import pandas as pd
import chardet
import sys
```

---

## Notes

* Maintain folder structure as-is to avoid path issues.
* `output.xlsx` is the final result file.
* Logging and retries are already integrated for unstable URLs.
* Scripts have been tested on:

  * **Python**: 3.12.6
  * **NLTK**: 3.9.1

---

## Project Structure

```
CODING_PART/
├───Extraction_Part
│   ├───earlier Scripts
│   ├───edge_driver
│   ├───extracted_articles_from_input_excel_2
│   ├───input
│   └───scraping_logs
└───Text_Analysis_Part
    ├───earlier_Scripts
    ├───extracted_articles_from_input_excel_2
    ├───MasterDictionary
    ├───nltk_data
    │   ├───corpora
    │   │   └───stopwords
    │   └───tokenizers
    └───output
```
# 🤖 Intelligent Resume Ranking System

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-Enabled-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An advanced, feature-rich Python web application designed to automatically parse, evaluate, and rank candidate resumes against specific job descriptions. Using Natural Language Processing (NLP) techniques, TF-IDF Vectorization, and Cosine Similarity, the system provides recruiting teams with data-driven insights to find the best talent efficiently.

The app features a multi-format file parser, smart contact info extraction, sublinear term-frequency scaling to prevent keyword stuffing, programming symbol preservation, and interactive gap analysis.

---

## 🌟 Key Features

*   **📄 Multi-Format Resume Parser**:
    *   **PDF Parsing**: Reads text from PDF files using `pypdf`.
    *   **Word & Text**: Seamlessly handles `.docx` via `python-docx` and `.txt` files.
*   **🔍 Smart Contact Info Extraction**: Employs robust regex patterns to automatically parse candidate email addresses and phone numbers.
*   **🛡️ Anti-Keyword Stuffing Mechanism**: Utilizes logarithmic term scaling (`sublinear_tf=True` in TF-IDF Vectorizer) so candidates cannot artificially inflate their ranking scores by repeating keywords.
*   **💻 Technical Keyword Preservation**: Features custom tokenizer patterns to preserve essential developer/engineering keywords like `C++`, `C#`, `.NET`, and `Node.js` that standard tokenizers strip away.
*   **📊 Interactive Visualizations**: Renders rich Plotly charts showing score distributions and candidate comparisons.
*   **🎯 Skill Gap Analysis**: Shows exact matched and missing keywords for any selected candidate, highlighting strengths and missing requirements.
*   **📥 Data Export**: Allows downloading full results in CSV format for seamless integration with ATS (Applicant Tracking Systems).

---

## 🏗️ Project Architecture & Components

The codebase utilizes a highly modular architectural pattern to isolate concerns and ensure extensibility:

```text
Intelligent-Resume-Ranking-System/
├── .venv/                      # Python Virtual Environment
├── requirements.txt            # Package dependencies
├── setup.bat                   # Automated environment setup script for Windows
├── app.py                      # Application entrypoint & Streamlit coordinator
├── resume_parser.py            # Resume file reader & regex parsers
├── ranker.py                   # Pre-processing, TF-IDF, and similarity calculations
├── README.md                   # Project documentation
└── sample_data/                # Folder structures for sample files
    ├── job_descriptions/       # Sample job requirements (.txt files)
    └── resumes/                # Realistic candidate resumes (.pdf files)
```

### Module Descriptions
*   **`app.py`**: Orchestrates UI presentation, handling multi-step wizards, file uploads, score distribution visualizations, and detailed candidate reviews.
*   **`resume_parser.py`**: Houses core text-extraction logic for PDFs, Word files, and text documents, alongside contact parsing using advanced regex patterns.
*   **`ranker.py`**: Performs text pre-processing (cleaning and custom tokenization keeping tech symbols), constructs TF-IDF vectors using sublinear scaling, and computes Cosine Similarity scoring.
*   **`setup.bat`**: Simplifies the startup flow on Windows by automating `.venv` creation, pip upgrades, dependency installation, and directories creation.

---

## ⚙️ Quick Start & Setup Instructions

### Prerequisites
Make sure you have the following installed on your system:
*   **Python 3.8 or higher**
*   **Git**

---

### 💻 Step-by-Step Installation

#### 1. Clone the Repository
Open your terminal (macOS/Linux) or Command Prompt/PowerShell (Windows) and run:
```bash
git clone https://github.com/Uttkarsh55/Intelligent-Resume-Ranking-System.git
cd Intelligent-Resume-Ranking-System
```

#### 2. Set Up a Virtual Environment
It is highly recommended to use a virtual environment to avoid dependency conflicts.

*   **macOS / Linux**:
    ```bash
    python3 -m venv .venv
    ```
*   **Windows**:
    ```bash
    python -m venv .venv
    ```

#### 3. Activate the Virtual Environment
Activate the environment you just created.

*   **macOS / Linux**:
    ```bash
    source .venv/bin/activate
    ```
*   **Windows (Command Prompt)**:
    ```bash
    .venv\Scripts\activate.bat
    ```
*   **Windows (PowerShell)**:
    ```bash
    .\.venv\Scripts\Activate.ps1
    ```

#### 4. Install Required Dependencies
Once the virtual environment is active, upgrade `pip` and install all the project requirements:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 🏃 Running the Application

To launch the web interface, run the following command in your terminal (with the virtual environment still active):
```bash
streamlit run app.py
```

This will automatically open the application in your default web browser. If it doesn't, navigate to the local URL shown in your terminal (usually `http://localhost:8501`).

---

### ⚡ Automated Windows Setup (Alternative)
If you are on Windows, you can automate virtual environment creation and package installation by simply double-clicking the `setup.bat` file in the project folder. Once the script finishes, run:
```bash
.venv\Scripts\activate
streamlit run app.py
```

---

## 💡 How to Interact with the System

1.  **Define Job Description (Step 1)**:
    Paste your target Job Description into the text area. The system will automatically run key-term TF-IDF calculations when you continue.
2.  **Upload Candidate Resumes (Step 2)**:
    Upload single or multiple resumes (`.pdf`, `.docx`, or `.txt`). Click **Analyze & Rank** to initiate text parsing and vectorization.
3.  **Explore Rankings (Step 3)**:
    *   Review the final ranked leaderboard showing names, similarity scores, email, and phone numbers.
    *   Interact with the **Score Distribution** Plotly chart to visually compare candidate fit.
4.  **Perform Skill Gap Analysis**:
    Select any candidate from the dropdown list to view exact matched keywords vs. missing keywords to guide interview questioning.
5.  **Export Results**:
    Click the **Export Results (CSV)** button to download the rankings data table.

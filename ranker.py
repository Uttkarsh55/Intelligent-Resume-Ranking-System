import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

# A list of standard English stop words + common Resume/Job Description filler words
STOP_WORDS = {
    # Standard English Stop Words
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'arent', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'cant', 'cannot', 'could',
    'couldnt', 'did', 'didnt', 'do', 'does', 'doesnt', 'doing', 'dont', 'down', 'during', 'each', 'few', 'for', 'from',
    'further', 'had', 'hadnt', 'has', 'hasnt', 'have', 'havent', 'having', 'he', 'hed', 'hell', 'hes', 'her', 'here',
    'heres', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'hows', 'i', 'id', 'ill', 'im', 'ive', 'if', 'in',
    'into', 'is', 'isnt', 'it', 'its', 'itself', 'lets', 'me', 'more', 'most', 'mustnt', 'my', 'myself', 'no', 'nor',
    'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
    'same', 'shanant', 'she', 'shed', 'shell', 'shes', 'should', 'shouldnt', 'so', 'some', 'such', 'than', 'that',
    'thats', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'theres', 'these', 'they', 'theyd',
    'theyll', 'theyre', 'theyve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was',
    'wasnt', 'we', 'wed', 'well', 'were', 'weve', 'werent', 'what', 'whats', 'when', 'whens', 'where', 'wheres',
    'which', 'while', 'who', 'whos', 'whom', 'why', 'whys', 'with', 'wont', 'would', 'wouldnt', 'you', 'youd',
    'youll', 'youre', 'youve', 'your', 'yours', 'yourself', 'yourselves',
    # Job Description Specific Stop Words (Filler terms that aren't skills)
    'experience', 'years', 'time', 'work', 'working', 'team', 'teams', 'skills', 'skill', 'ability', 'knowledge',
    'understanding', 'strong', 'excellent', 'good', 'required', 'preferred', 'requirements', 'responsibilities',
    'role', 'opportunity', 'company', 'candidate', 'candidates', 'looking', 'join', 'help', 'build', 'create',
    'design', 'development', 'develop', 'including', 'using', 'must', 'plus', 'familiarity', 'hands', 'on', 'proven',
    'track', 'record', 'fast', 'paced', 'high', 'quality', 'solutions', 'degree', 'bachelor', 'master', 'phd',
    'computer', 'science', 'related', 'field', 'equivalent', 'business', 'services', 'techniques', 'project',
    'projects', 'environment', 'support', 'management', 'manage', 'managing', 'provide', 'providing', 'ensure',
    'ensuring', 'best', 'practices', 'new', 'existing', 'system', 'systems', 'application', 'applications', 'software',
    'hardware', 'technical', 'technology', 'tools', 'process', 'processes', 'methodologies', 'learning', 'models', 'industry'
}

def clean_text(text):
    """
    Cleans and preprocesses the text for TF-IDF.
    Lowercases, removes special characters (while preserving programming terms like C++, C#),
    removes extra whitespace, and strips stop words.
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Clean email addresses and phone numbers to focus on skill content
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', text)
    text = re.sub(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,4}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '', text)
    
    # Replace special characters but preserve + and # (for C++, C#) and common punctuation
    # We replace symbols that aren't letters, digits, spaces, +, or #
    text = re.sub(r'[^\w\s\+#\-\.]', ' ', text)
    
    # Split text into tokens and filter out stop words and short terms
    tokens = text.split()
    cleaned_tokens = []
    for token in tokens:
        # Strip trailing dots or hyphens from tokens
        token = token.strip('.-')
        if token and token not in STOP_WORDS and len(token) > 1:
            cleaned_tokens.append(token)
            
    return " ".join(cleaned_tokens)

def rank_resumes(jd_text, resumes):
    """
    Computes similarity scores for multiple resumes against a job description.
    
    Parameters:
    - jd_text (str): The raw text of the job description.
    - resumes (list of dict): List of resume dicts containing:
        {
            "id": unique_id,
            "file_name": name_of_file,
            "raw_text": extracted_text,
            "candidate_info": dict of parsed details
        }
        
    Returns:
    - df_results (DataFrame): Ranked candidates with similarity score and metadata.
    - top_keywords (list): Top keywords extracted from the JD.
    """
    if not jd_text or not resumes:
        return pd.DataFrame(), []
    
    # Clean the job description
    cleaned_jd = clean_text(jd_text)
    
    # Clean all resumes
    cleaned_resumes = [clean_text(res["raw_text"]) for res in resumes]
    
    # We combine the clean JD and clean resumes for fitting the vectorizer
    all_docs = [cleaned_jd] + cleaned_resumes
    
    # Define vectorizer.
    # Crucial details:
    # 1. We use a custom token_pattern to keep 'c++' and 'c#' intact
    # 2. We use sublinear_tf=True to scale term frequencies logarithmically, which works better for resumes
    #    (otherwise a resume repeating "python" 50 times gets artificially boosted).
    vectorizer = TfidfVectorizer(
        token_pattern=r'(?u)\b[\w+#-]{2,}\b',
        sublinear_tf=True,
        stop_words='english'
    )
    
    # Fit and transform the documents
    tfidf_matrix = vectorizer.fit_transform(all_docs)
    
    # The first row is the job description
    jd_vector = tfidf_matrix[0]
    
    # The remaining rows are the resumes
    resume_vectors = tfidf_matrix[1:]
    
    # Compute Cosine Similarity between the JD and all resumes
    similarities = cosine_similarity(resume_vectors, jd_vector).flatten()
    
    # Extract top keywords from the Job Description
    # We find the feature names and their corresponding TF-IDF weights in the JD vector
    feature_names = np.array(vectorizer.get_feature_names_out())
    jd_dense = jd_vector.todense().A1
    
    # Sort features by TF-IDF weight in descending order
    sorted_indices = np.argsort(jd_dense)[::-1]
    # Filter out features with 0 weight
    top_keywords_with_weights = [
        (feature_names[i], float(jd_dense[i]))
        for i in sorted_indices if jd_dense[i] > 0
    ]
    
    # We take the top 15 terms as the main JD keywords
    top_keywords = [kw for kw, weight in top_keywords_with_weights[:15]]
    
    # Build the results table
    results = []
    for idx, resume in enumerate(resumes):
        score = float(similarities[idx])
        # Convert to match percentage (0 to 100)
        match_percentage = round(score * 100, 1)
        
        # Analyze keyword overlap
        resume_clean_text = cleaned_resumes[idx]
        matched_kws = []
        missing_kws = []
        
        # Match using word boundaries or sub-string checks for C++ / C#
        for kw in top_keywords:
            escaped_kw = re.escape(kw)
            if '+' in kw or '#' in kw:
                pattern = rf'(?i)(?:^|[\s,;.]){escaped_kw}(?:$|[\s,;.])'
            else:
                pattern = rf'(?i)\b{escaped_kw}\b'
                
            if re.search(pattern, resume_clean_text):
                matched_kws.append(kw)
            else:
                missing_kws.append(kw)
                
        # Calculate a simple keyword match score
        kw_match_rate = round((len(matched_kws) / len(top_keywords)) * 100, 1) if top_keywords else 0.0
        
        # Generate a Match Reason
        if kw_match_rate >= 80:
            reason = f"Excellent fit. Matches {len(matched_kws)} key requirements including {', '.join(matched_kws[:3])}."
        elif kw_match_rate >= 50:
            reason = f"Strong fit. Matches core requirements but missing {', '.join(missing_kws[:2])}."
        elif kw_match_rate >= 20:
            reason = f"Partial fit. Has some relevant skills but lacks {len(missing_kws)} key requirements."
        else:
            reason = f"Low fit. Missing most technical requirements for this role."
        
        results.append({
            "Rank": 0,  # Will assign after sorting
            "Candidate Name": resume["candidate_info"]["name"],
            "Email": resume["candidate_info"]["email"],
            "Phone": resume["candidate_info"]["phone"],
            "Skills": ", ".join(resume["candidate_info"]["skills"][:10]),  # Top 10 extracted skills
            "Match Score": match_percentage,
            "Keyword Match Rate": kw_match_rate,
            "Match Reason": reason,
            "Matched Keywords": matched_kws,
            "Missing Keywords": missing_kws,
            "File Name": resume["file_name"],
            "Raw Text": resume["raw_text"]
        })
        
    # Sort by Match Score descending
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        df_results = df_results.sort_values(by="Match Score", ascending=False).reset_index(drop=True)
        # Assign ranks
        df_results["Rank"] = df_results.index + 1
        
    return df_results, top_keywords

def rank_resumes_bert(jd_text, resumes):
    if not jd_text or not resumes:
        return pd.DataFrame(), []
        
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("SentenceTransformer not installed.")
        return pd.DataFrame(), []
        
    # Get keywords and basic parsing from TF-IDF
    df_tfidf, top_keywords = rank_resumes(jd_text, resumes)
    if df_tfidf.empty:
        return pd.DataFrame(), []
        
    # Load model (this will download weights the first time)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Use raw text for BERT as it understands natural sentence context
    jd_raw = jd_text
    resume_raws = [res["raw_text"] for res in resumes]
    
    all_docs = [jd_raw] + resume_raws
    embeddings = model.encode(all_docs)
    
    jd_vector = embeddings[0:1]
    resume_vectors = embeddings[1:]
    
    similarities = cosine_similarity(resume_vectors, jd_vector).flatten()
    
    results = []
    for idx, resume in enumerate(resumes):
        score = float(similarities[idx])
        # BERT cosine similarity can sometimes be slightly negative or weird, ensure 0-100
        match_percentage = round(max(0, score) * 100, 1)
        
        file_name = resume["file_name"]
        row = df_tfidf[df_tfidf["File Name"] == file_name].iloc[0]
        
        results.append({
            "Rank": 0,
            "Candidate Name": row["Candidate Name"],
            "Email": row["Email"],
            "Phone": row["Phone"],
            "Skills": row["Skills"],
            "Match Score": match_percentage,
            "Keyword Match Rate": row["Keyword Match Rate"],
            "Match Reason": f"Semantic Match Score: {match_percentage}%. (Evaluated using Deep Learning Sentence-BERT)",
            "Matched Keywords": row["Matched Keywords"],
            "Missing Keywords": row["Missing Keywords"],
            "File Name": file_name,
            "Raw Text": row["Raw Text"]
        })
        
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        df_results = df_results.sort_values(by="Match Score", ascending=False).reset_index(drop=True)
        df_results["Rank"] = df_results.index + 1
        
    return df_results, top_keywords

import os
import pickle
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from DB.connection import connect_db

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
PLAGIARISM_THRESHOLD = float(os.getenv("PLAGIARISM_THRESHOLD", "0.85"))

def load_code(input_data, is_file=False):
    """
    Load code from file path or direct text input.
    
    """
    if is_file:
        with open(input_data, 'r', encoding='utf-8') as f:
            return f.read()
    return input_data


def generate_embedding(code_text):
    """
    Generate embedding vector for code using Gemini.
    
    """
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=code_text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def store_embedding(submission_id, embedding_vector, db_path=None):
    """
    Store embedding vector in database.

    """
    if embedding_vector is None:
        raise ValueError("Cannot store None embedding")
    
    conn = connect_db(db_path)
    c = conn.cursor()
    
    vector_serialized = pickle.dumps(embedding_vector)
    dimension = len(embedding_vector)
    created_at = datetime.utcnow()
    
    c.execute("""
        INSERT INTO embeddings (submission_id, vector_ref, model_version, dimension, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (submission_id, vector_serialized, EMBEDDING_MODEL, dimension, created_at))
    
    conn.commit()
    conn.close()


def get_embedding(submission_id, db_path=None):
    """
    Retrieve embedding vector from database.
    
    """
    conn = connect_db(db_path)
    c = conn.cursor()
    
    c.execute("""
        SELECT vector_ref FROM embeddings 
        WHERE submission_id = ?
    """, (submission_id,))
    
    row = c.fetchone()
    conn.close()
    
    if row:
        return pickle.loads(row[0])
    return None


def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors.
    
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def process_submission_embedding(submission_id, input_data, is_file=False):
    """
    Complete workflow: load code, generate embedding, store in DB.

    """
    code_text = load_code(input_data, is_file)
    embedding_vector = generate_embedding(code_text)
    
    if embedding_vector:
        store_embedding(submission_id, embedding_vector)
        print(f"Embedding stored for submission {submission_id}, dimension={len(embedding_vector)}")
    else:
        print(f"Failed to generate embedding for submission {submission_id}")
    
    return embedding_vector


def check_similarity_with_submissions(submission_id, assignment_id, threshold=None, db_path=None):
    """
    Compare submission with all other submissions in the same assignment.

    """
    if threshold is None:
        threshold = PLAGIARISM_THRESHOLD
    
    conn = connect_db(db_path)
    c = conn.cursor()
    
    current_embedding = get_embedding(submission_id, db_path)
    if not current_embedding:
        conn.close()
        return []
    
    c.execute("""
        SELECT s.id, e.vector_ref, s.student_id
        FROM submissions s
        JOIN embeddings e ON s.id = e.submission_id
        WHERE s.assignment_id = ? AND s.id != ?
    """, (assignment_id, submission_id))
    
    similar_submissions = []
    
    for row in c.fetchall():
        other_id, vector_blob, student_id = row
        other_embedding = pickle.loads(vector_blob)
        
        similarity = cosine_similarity(current_embedding, other_embedding)
        
        if similarity >= threshold:
            similar_submissions.append({
                'submission_id': other_id,
                'student_id': student_id,
                'similarity': similarity,
                'percentage': f"{similarity * 100:.1f}%"
            })
    
    conn.close()
    return similar_submissions


if __name__ == "__main__":
    example_submission_id = 1
    example_code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
"""
    
    print("Processing example submission...")
    embedding = process_submission_embedding(example_submission_id, example_code, is_file=False)
    
    if embedding:
        print(f"Success! Generated {len(embedding)}-dimensional embedding")
    
    retrieved = get_embedding(example_submission_id)
    if retrieved:
        print(f"Retrieved embedding has {len(retrieved)} dimensions")
        print(f"Embeddings match: {np.allclose(embedding, retrieved)}")
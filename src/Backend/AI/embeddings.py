import sqlite3
import pickle
from datetime import datetime
from sentence_transformers import SentenceTransformer
from DB.connection import connect_db

# Initialize model (CPU-friendly)
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

def embed_code(code_text: str):
    """
    Generate embedding vector for a given code string.
    Works for code + comments.
    """
    return model.encode(code_text)

def save_embedding(submission_id: int, vector, db_path=None):
    """
    Save embedding vector in the embeddings table.
    vector: numpy array or list
    """
    conn = connect_db(db_path)
    c = conn.cursor()
    vector_serialized = pickle.dumps(vector)  # store as BLOB
    dimension = len(vector)
    created_at = datetime.utcnow()
    
    c.execute("""
        INSERT INTO embeddings (submission_id, vector_ref, model_version, dimension, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (submission_id, vector_serialized, MODEL_NAME, dimension, created_at))
    
    conn.commit()
    conn.close()

def process_submission(submission_id: int, code_text: str):
    """
    Main function: generate embedding and save to DB
    """
    vector = embed_code(code_text)
    save_embedding(submission_id, vector)
    print(f"Embedding saved for submission {submission_id}, dimension={len(vector)}")

# Example usage
if __name__ == "__main__":
    # Replace with actual submission fetching logic
    example_submission_id = 1
    example_code = """
    def add(a, b):
        # This function returns sum of two numbers
        return a + b
    """
    process_submission(example_submission_id, example_code)

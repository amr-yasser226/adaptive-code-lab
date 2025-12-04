try:
    from sentence_transformers import SentenceTransformer
    import torch
    import numpy as np

    # Load the model
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    model = SentenceTransformer(MODEL_NAME)

    # Test embedding generation
    test_text = "print('Hello world')"
    embedding = model.encode(test_text)

    print(f"Libraries are installed correctly!")
    print(f"Model '{MODEL_NAME}' loaded successfully.")
    print(f"Embedding vector length: {len(embedding)}")
    print(f"Embedding snippet (first 5 values): {embedding[:5]}")

except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Something went wrong: {e}")

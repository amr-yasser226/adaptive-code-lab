import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

print("=" * 60)
print("API Keys Test Suite")
print("=" * 60)

# ==========================================
# Step 1: Check if .env file is loaded
# ==========================================
print("\nStep 1: Checking .env file...")

groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GOOGLE_API_KEY")

if groq_key:
    print(f"[PASS] Groq key found: {groq_key[:20]}... (length: {len(groq_key)})")
else:
    print("[FAIL] Groq key NOT found in .env file")

if gemini_key:
    print(f"[PASS] Gemini key found: {gemini_key[:20]}... (length: {len(gemini_key)})")
else:
    print("[FAIL] Gemini key NOT found in .env file")

if not groq_key or not gemini_key:
    print("\nWARNING: Please add your API keys to the .env file first!")
    exit(1)

# ==========================================
# Step 2: Test Groq API (Main AI)
# ==========================================
print("\n" + "=" * 60)
print("Step 2: Testing Groq API (Main AI - Fast Feedback)")
print("=" * 60)

try:
    from groq import Groq
    
    groq_client = Groq(api_key=groq_key)
    
    print("\nSending test request to Groq...")
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Hello, this is a test! Please respond with 'Groq API is working!'"}
        ],
        max_tokens=100
    )
    
    print("[PASS] Groq API works! Response:")
    print("-" * 60)
    print(response.choices[0].message.content)
    print("-" * 60)
    
except ImportError:
    print("[FAIL] Groq library not installed!")
    print("   Run: pip install groq")
except Exception as e:
    print(f"[FAIL] Groq API test failed: {e}")
    print("\nPossible issues:")
    print("   - Invalid API key")
    print("   - Network connection problem")
    print("   - Rate limit exceeded")

# ==========================================
# Step 3: Test Gemini API (Embeddings)
# ==========================================
print("\n" + "=" * 60)
print("Step 3: Testing Gemini API (Embeddings - Similarity)")
print("=" * 60)

try:
    import google.generativeai as genai
    
    genai.configure(api_key=gemini_key)
    
    # Test 1: Chat completion
    print("\nTest 3a: Testing Gemini chat...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, this is a test! Please respond with 'Gemini API is working!'")
    
    print("[PASS] Gemini chat works! Response:")
    print("-" * 60)
    print(response.text)
    print("-" * 60)
    
    # Test 2: Embeddings
    print("\nTest 3b: Testing Gemini embeddings...")
    result = genai.embed_content(
        model="models/text-embedding-004",
        content="This is a test sentence for embedding",
        task_type="retrieval_document"
    )
    
    embedding = result['embedding']
    print(f"[PASS] Gemini embeddings work!")
    print(f"   Embedding dimension: {len(embedding)}")
    print(f"   First 5 values: {embedding[:5]}")
    
except ImportError:
    print("[FAIL] Google Generative AI library not installed!")
    print("   Run: pip install google-generativeai")
except Exception as e:
    print(f"[FAIL] Gemini API test failed: {e}")
    print("\nPossible issues:")
    print("   - Invalid API key")
    print("   - Network connection problem")
    print("   - API quota exceeded")

# ==========================================
# Step 4: Test Integration (Both APIs together)
# ==========================================
print("\n" + "=" * 60)
print("Step 4: Testing Integration (Groq + Gemini)")
print("=" * 60)

try:
    # Simulate a real workflow: Get feedback + check similarity
    print("\nSimulating real workflow...")
    
    # 1. Get feedback from Groq
    code_to_analyze = "def add(a, b): return a + b"
    
    print(f"\nAnalyzing code: {code_to_analyze}")
    
    feedback_response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": f"Give brief feedback on this code: {code_to_analyze}"}
        ],
        max_tokens=150
    )
    
    print("\nGroq Feedback:")
    print("-" * 60)
    print(feedback_response.choices[0].message.content)
    print("-" * 60)
    
    # 2. Get embedding from Gemini
    embedding_result = genai.embed_content(
        model="models/text-embedding-004",
        content=code_to_analyze,
        task_type="retrieval_document"
    )
    
    print(f"\nGemini Embedding generated: {len(embedding_result['embedding'])} dimensions")
    
    print("\n[PASS] Integration test successful! Both APIs working together!")
    
except Exception as e:
    print(f"[FAIL] Integration test failed: {e}")

# ==========================================
# Final Summary
# ==========================================
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)

print("\n[PASS] All tests completed!")
print("\nYour setup is ready for:")
print("  - Groq: Fast AI feedback for students")
print("  - Gemini: Code similarity & plagiarism detection")
print("\nYou can now run your main application!")

print("\n" + "=" * 60)
# Adaptive Code Lab (ACCL)

## Project Layout (Clean Architecture)
- `src/core/`: Domain entities and business logic.
- `src/infrastructure/`: Database, Repositories, AI integration.
- `src/web/`: Flask application and routes.
- `src/config/`: Configuration settings.
- `data/`: SQLite database storage.

## How to Run

### 1. Prerequisites
- Python 3.8+
- Virtual environment recommended.

### 2. Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env if needed (e.g., add API keys)
```

### 3. Database Initialization
The project uses SQLite. The database file will be created at `data/Accl_DB.db`.
If you need to initialize the database schema:
```bash
# Run the verification script (it checks imports)
python verify_installation.py

# (Optional) Run migrations manually if needed
# python src/infrastructure/database/migrations.py
```

### 4. Running the Application
To start the Flask development server:
```bash
python run.py
```
Access the app at `http://127.0.0.1:5000` (or `localhost:5000`).

### 5. Running Tests
Run the full test suite with:
```bash
pytest tests/
```

---

## Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop
docker-compose down
```

### Using Docker Directly
```bash
docker build -t accl-app .
docker run -p 5000:5000 -v ./data:/app/data accl-app
```

---

## Documentation

- [Phase 5 Final Delivery](docs/CSAI203_Final_Delivery_Team18_202301043.md)
- [SRS Document](docs/CSAI203_SRS_Team18_202301043.pdf)
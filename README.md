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
# Initialize database and seed initial data
python -m infrastructure.database.create_db
```

### 4. Running the Application
To start the Flask development server:
```bash
python run.py
```
Access the app at `http://127.0.0.1:5000`.

### 5. Running Tests
Run the full test suite (including new Phase 5 edge cases):
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

## Troubleshooting & Edge Cases (Phase 5)

The application has been robustified against several critical failure modes:

- **Database Failures**: Handled via standardized `sqlite3.Error` catching in web routes. If the database is inaccessible, users are notified via flashed messages.
- **AI Provider Failures**: `GeminiClient` and `GroqClient` catch API errors (rate limits, connection issues) and propagate them gracefully as `RuntimeError`.
- **Malformed API Input**: All API endpoints (code testing, hints, drafts) now validate JSON inputs and return appropriate `400` or `500` errors instead of crashing.

---

## UI Customization (Educational Tech Theme)

The application uses a refined **Educational Tech Theme** (Blues & Purples). You can customize the entire look by modifying the `:root` variables in `src/web/static/css/main.css`:

- `--brand-primary`: Main theme color (Indigo/Blue).
- `--brand-secondary`: Secondary theme color (Purple).
- `--glass-*`: Glassmorphism effects for a premium feel.

---

## Documentation

- [Phase 5 Final Delivery](docs/CSAI203_Final_Delivery_Team18_202301043.md)
- [SRS Document](docs/CSAI203_SRS_Team18_202301043.pdf)
- [Development Walkthrough](file:///home/amr-yasser/.gemini/antigravity/brain/71760fa3-8867-4469-8443-05f3120a104f/walkthrough.md)
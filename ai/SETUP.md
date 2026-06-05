# Setup Guide - Vietnamese NLP Intent Classification Server

This guide will help you set up the development environment for the Vietnamese NLP Intent Classification Server.

## Prerequisites

- **Python 3.9 or higher** (Python 3.14.2 detected on your system ✅)
- **pip** package manager
- **Git** (for version control)
- **(Optional)** CUDA-capable GPU for faster model training and inference

## Quick Start

### 1. Navigate to the AI directory

```bash
cd ai
```

### 2. Create a virtual environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages including:
- FastAPI and Uvicorn (web framework)
- Transformers and PyTorch (ML models)
- Hypothesis and Pytest (testing)
- And all other dependencies

### 4. Set up environment variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# On Windows: notepad .env
# On Linux/Mac: nano .env
```

**Important:** Change the `JWT_SECRET_KEY` to a secure random string in production!

### 5. Verify installation

Run the sample tests to verify everything is installed correctly:

```bash
pytest tests/unit/test_sample.py -v
```

Expected output:
```
tests/unit/test_sample.py::test_sample_addition PASSED
tests/unit/test_sample.py::test_sample_string PASSED
tests/unit/test_sample.py::test_sample_with_marker PASSED
```

### 6. Start the development server

**Windows:**
```bash
run_dev.bat
```

**Linux/Mac:**
```bash
chmod +x run_dev.sh
./run_dev.sh
```

**Or manually:**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### 7. Test the server

Open your browser and navigate to:
- **API Root:** http://localhost:8001/
- **Health Check:** http://localhost:8001/health
- **API Documentation:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

You should see the API documentation and be able to test endpoints.

## Project Structure Overview

```
ai/
├── src/                    # Source code
│   ├── api/               # FastAPI endpoints and middleware
│   ├── classifiers/       # Intent classifiers (rule-based, ML-based, hybrid)
│   ├── preprocessing/     # Text preprocessing pipeline
│   ├── entities/          # Entity extraction logic
│   ├── models/            # ML model definitions
│   ├── training/          # Model training scripts
│   ├── utils/             # Utility functions
│   ├── config/            # Configuration (settings.py, schema.py)
│   └── main.py            # FastAPI application entry point
├── tests/                 # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── property/         # Property-based tests (Hypothesis)
├── models/               # Trained model artifacts (.pt, .onnx files)
├── data/                 # Training and test data
│   ├── raw/             # Raw training data
│   ├── processed/       # Processed datasets (train/val/test)
│   └── augmented/       # Augmented training data
├── scripts/             # Utility scripts (training, evaluation, etc.)
├── logs/                # Application logs
├── requirements.txt     # Python dependencies
├── pytest.ini          # Pytest configuration
├── .env.example        # Environment variables template
├── Dockerfile          # Docker container definition
├── docker-compose.yml  # Docker Compose configuration
└── README.md           # Project documentation
```

## Next Steps

After completing the setup, you can proceed with:

1. **Task 1.2:** Set up configuration management
2. **Task 1.3:** Create Docker configuration (already done!)
3. **Task 2:** Implement data models and schema
4. **Task 3:** Implement preprocessing pipeline
5. And so on...

Refer to the `tasks.md` file in `.kiro/specs/vietnamese-nlp-intent-classification/` for the complete task list.

## Common Issues

### Issue: `pip install` fails with SSL errors

**Solution:** Upgrade pip and try again:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: PyTorch installation is slow or fails

**Solution:** Install PyTorch separately first:
```bash
# CPU version (faster download)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install other dependencies
pip install -r requirements.txt
```

### Issue: Port 8001 is already in use

**Solution:** Change the port in `.env` file:
```
API_PORT=8002
```

Or specify a different port when running:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8002
```

### Issue: Import errors when running tests

**Solution:** Make sure you're in the `ai/` directory and the virtual environment is activated:
```bash
cd ai
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pytest
```

## Docker Setup (Alternative)

If you prefer using Docker:

### 1. Build the Docker image

```bash
docker-compose build
```

### 2. Start all services (NLP server, PostgreSQL, Redis)

```bash
docker-compose up -d
```

### 3. View logs

```bash
docker-compose logs -f nlp-server
```

### 4. Stop services

```bash
docker-compose down
```

## Development Workflow

1. **Activate virtual environment** (if not already activated)
2. **Make code changes** in `src/` directory
3. **Write tests** in `tests/` directory (TDD approach)
4. **Run tests** with `pytest`
5. **Start dev server** with hot reload to test changes
6. **Commit changes** to version control

## Testing

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

### Run specific test categories:
```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m property      # Property-based tests only
```

### Run specific test file:
```bash
pytest tests/unit/test_sample.py -v
```

## Getting Help

- **Project Documentation:** See `README.md`
- **Requirements:** See `.kiro/specs/vietnamese-nlp-intent-classification/requirements.md`
- **Design:** See `.kiro/specs/vietnamese-nlp-intent-classification/design.md`
- **Tasks:** See `.kiro/specs/vietnamese-nlp-intent-classification/tasks.md`

## Success! ✅

If you've completed all the steps above and the server is running, you're ready to start implementing the NLP features!

The basic project structure is now set up and ready for development.

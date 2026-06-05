# Vietnamese NLP Intent Classification Server

AI-powered Natural Language Processing server for Vietnamese Smart Home intent classification and entity extraction.

## Overview

This NLP server transforms natural Vietnamese language input into structured intents with extracted entities for Smart Home automation. It serves as the natural language understanding layer between users and the IoT backend.

### Key Features

- **Intent Classification**: Classifies 15 core intent categories from Vietnamese natural language
- **Entity Extraction**: Extracts structured parameters (device, action, location, etc.)
- **Hybrid Approach**: Combines rule-based (fast) and ML-based (accurate) classification
- **PhoBERT Model**: Fine-tuned Vietnamese language model for high accuracy
- **Context-Aware**: Supports device context for improved classification
- **Property-Based Testing**: Comprehensive testing with Hypothesis framework

### Architectural Boundary

**NLP Server Responsibilities:**
- Intent classification from Vietnamese natural language
- Entity extraction according to predefined schema
- Confidence scoring and fallback handling
- Returning structured Intent_Response

**Backend Decision Engine Responsibilities (NOT this server):**
- Reasoning logic based on intent and entities
- Sensor data validation and checking
- Device selection based on context
- Automation execution and MQTT commands

## Project Structure

```
ai/
├── src/                    # Source code
│   ├── api/               # FastAPI endpoints and middleware
│   ├── classifiers/       # Rule-based, ML-based, and hybrid classifiers
│   ├── preprocessing/     # Text preprocessing pipeline
│   ├── entities/          # Entity extraction logic
│   ├── models/            # ML model definitions
│   ├── training/          # Model training scripts
│   ├── utils/             # Utility functions
│   └── config/            # Configuration management
├── tests/                 # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── property/         # Property-based tests (Hypothesis)
├── models/               # Model artifacts (trained models)
├── data/                 # Training and test data
│   ├── raw/             # Raw training data
│   ├── processed/       # Processed datasets
│   └── augmented/       # Augmented training data
├── scripts/             # Utility scripts
│   ├── train_model.py   # Model training script
│   ├── evaluate.py      # Model evaluation script
│   └── export_onnx.py   # ONNX export script
├── requirements.txt     # Python dependencies
├── pytest.ini          # Pytest configuration
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Setup

### Prerequisites

- Python 3.9 or higher
- pip package manager
- (Optional) CUDA-capable GPU for faster inference

### Installation

1. **Create virtual environment:**
   ```bash
   cd ai
   python -m venv .venv
   ```

2. **Activate virtual environment:**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Configuration

Create a `.env` file with the following variables:

```env
# API Configuration
API_VERSION=v1
API_HOST=0.0.0.0
API_PORT=8001
DEBUG=False

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/nlp_db

# Redis Cache
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=300

# Model Configuration
MODEL_PATH=models/phobert_intent_classifier.pt
ONNX_MODEL_PATH=models/phobert_intent_classifier.onnx
USE_ONNX=True
CONFIDENCE_THRESHOLD=0.7

# Performance
MAX_CONCURRENT_REQUESTS=50
INFERENCE_TIMEOUT_SECONDS=5
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/nlp_server.log
LOG_ROTATION_DAYS=30
```

## Usage

### Running the Server

**Development mode:**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

**Production mode:**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8001 --workers 4
```

### API Endpoints

#### Classify Intent
```bash
POST /api/v1/intent/classify
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "text": "Bật đèn phòng khách",
  "user_id": "user123",
  "home_id": "home456",
  "device_context": {
    "current_room": "living_room",
    "available_devices": ["light", "fan", "ac"]
  }
}
```

**Response:**
```json
{
  "intent": "control_device",
  "entities": {
    "device": "light",
    "action": "turn_on",
    "location": "living_room"
  },
  "confidence": 0.98,
  "timestamp": "2024-01-15T10:30:00Z",
  "classifier_type": "rule"
}
```

#### Health Check
```bash
GET /health
```

#### Metrics (Prometheus)
```bash
GET /api/v1/metrics
```

## Testing

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

### Run property-based tests only:
```bash
pytest tests/property/ -v
```

### Run specific test file:
```bash
pytest tests/unit/test_preprocessing.py -v
```

## Model Training

### Prepare training data:
```bash
python scripts/prepare_dataset.py --input data/raw/training_data.json --output data/processed/
```

### Train model:
```bash
python scripts/train_model.py --config config/training_config.yaml
```

### Evaluate model:
```bash
python scripts/evaluate.py --model models/phobert_intent_classifier.pt --test-data data/processed/test.json
```

### Export to ONNX:
```bash
python scripts/export_onnx.py --model models/phobert_intent_classifier.pt --output models/phobert_intent_classifier.onnx
```

## Supported Intents

The system supports 15 core intent categories:

1. **control_device** - Device control with entities (device, action, location, value, unit)
2. **environmental_comfort** - Environmental comfort requests (cooling, warming, brighten, dim, ventilate)
3. **query_sensor** - Sensor data queries (temperature, humidity, rain, gas, fire, motion)
4. **query_device_status** - Device status queries
5. **security_mode** - Security mode changes (armed, disarmed)
6. **security_alert** - Security alerts (fire, gas, intrusion) with false positive prevention
7. **activate_scene** - Scene activation (sleep, wake_up, movie, away, home)
8. **weather_action** - Weather-responsive actions (rain, sunny)
9. **lock_all_doors** - Lock all doors command
10. **turn_off_all_devices** - Turn off all devices command
11. **create_automation** - Create new automation rule
12. **unknown** - Fallback intent for unrecognized input

## Performance Targets

- **MVP (no context)**: < 300ms CPU, < 100ms GPU (p50 and p95)
- **Advanced (with context)**: < 700ms CPU, < 200ms GPU
- **Rule-based classifier**: < 10ms
- **Concurrent requests**: 50+ simultaneous requests

## Development

### Code Style

The project follows PEP 8 style guidelines. Use the following tools:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Adding New Intents

1. Update `ENTITY_SCHEMA` in `src/config/schema.py`
2. Add training examples to `data/raw/training_data.json`
3. Add rule patterns to `src/classifiers/rule_based.py` (if applicable)
4. Retrain ML model with new data
5. Add unit tests and property tests
6. Update documentation

## Deployment

### Docker

```bash
# Build image
docker build -t nlp-server:latest .

# Run container
docker run -p 8001:8001 --env-file .env nlp-server:latest
```

### Docker Compose

```bash
docker-compose up -d
```

## Monitoring

- **Prometheus metrics**: Available at `/api/v1/metrics`
- **Logs**: Structured JSON logs in `logs/nlp_server.log`
- **Health check**: Available at `/health`

## License

[Your License Here]

## Contact

[Your Contact Information]

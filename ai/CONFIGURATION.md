# Configuration Guide

This document describes all configuration options for the Vietnamese NLP Intent Classification Server.

## Configuration Files

- **`.env`**: Environment-specific configuration (not committed to git)
- **`.env.example`**: Template with all available configuration options
- **`src/config/settings.py`**: Configuration schema and validation

## Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your specific values:
   ```bash
   nano .env  # or use your preferred editor
   ```

3. The application will automatically load settings from `.env` on startup.

## Configuration Sections

### API Configuration

Controls the API server behavior.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `API_VERSION` | string | `v1` | API version for endpoint paths |
| `API_HOST` | string | `0.0.0.0` | Host to bind the server to |
| `API_PORT` | integer | `8001` | Port to run the server on |
| `DEBUG` | boolean | `False` | Enable debug mode (verbose logging, auto-reload) |

**Example:**
```env
API_VERSION=v1
API_HOST=0.0.0.0
API_PORT=8001
DEBUG=False
```

### CORS Configuration

Controls Cross-Origin Resource Sharing for web clients.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CORS_ORIGINS` | string | `http://localhost:3000,...` | Comma-separated list of allowed origins |
| `CORS_ALLOW_CREDENTIALS` | boolean | `True` | Allow credentials in CORS requests |
| `CORS_ALLOW_METHODS` | string | `GET,POST` | Allowed HTTP methods |
| `CORS_ALLOW_HEADERS` | string | `Authorization,Content-Type` | Allowed HTTP headers |

**Example:**
```env
CORS_ORIGINS=http://localhost:3000,https://smarthome.example.com
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=GET,POST
CORS_ALLOW_HEADERS=Authorization,Content-Type
```

### JWT Authentication

Controls JSON Web Token authentication.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `JWT_SECRET_KEY` | string | `change-this-secret-key` | **IMPORTANT:** Secret key for JWT signing (change in production!) |
| `JWT_ALGORITHM` | string | `HS256` | Algorithm for JWT signing |
| `JWT_EXPIRATION_MINUTES` | integer | `60` | Token expiration time in minutes |

**Example:**
```env
JWT_SECRET_KEY=your-super-secret-key-min-32-characters-long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
```

**Security Note:** Generate a strong secret key for production:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Database Configuration

PostgreSQL database connection settings.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | string | `postgresql://user:password@localhost:5432/nlp_db` | PostgreSQL connection URL |

**Example:**
```env
DATABASE_URL=postgresql://nlp_user:secure_password@localhost:5432/nlp_production
```

**Format:** `postgresql://[user]:[password]@[host]:[port]/[database]`

### Redis Cache Configuration

Redis cache for performance optimization.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REDIS_URL` | string | `redis://localhost:6379/0` | Redis connection URL |
| `CACHE_TTL_SECONDS` | integer | `300` | Cache time-to-live in seconds (5 minutes) |

**Example:**
```env
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=300
```

### Model Configuration

ML model paths and inference settings.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MODEL_PATH` | string | `models/phobert_intent_classifier.pt` | Path to PyTorch model file |
| `ONNX_MODEL_PATH` | string | `models/phobert_intent_classifier.onnx` | Path to ONNX model file |
| `USE_ONNX` | boolean | `True` | Use ONNX Runtime for faster inference |
| `CONFIDENCE_THRESHOLD` | float | `0.7` | Minimum confidence score to accept classification |

**Example:**
```env
MODEL_PATH=models/phobert_intent_classifier.pt
ONNX_MODEL_PATH=models/phobert_intent_classifier.onnx
USE_ONNX=True
CONFIDENCE_THRESHOLD=0.7
```

**Notes:**
- ONNX Runtime provides ~2-3x faster inference than PyTorch
- Set `USE_ONNX=False` if ONNX model is not available
- Confidence threshold of 0.7 means 70% certainty required

### Performance Configuration

Controls server performance and resource limits.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MAX_CONCURRENT_REQUESTS` | integer | `50` | Maximum concurrent requests to handle |
| `INFERENCE_TIMEOUT_SECONDS` | integer | `5` | Timeout for model inference |
| `RATE_LIMIT_PER_MINUTE` | integer | `60` | Maximum requests per minute per user |

**Example:**
```env
MAX_CONCURRENT_REQUESTS=50
INFERENCE_TIMEOUT_SECONDS=5
RATE_LIMIT_PER_MINUTE=60
```

**Tuning Tips:**
- Increase `MAX_CONCURRENT_REQUESTS` for high-traffic scenarios
- Decrease `INFERENCE_TIMEOUT_SECONDS` for faster failure detection
- Adjust `RATE_LIMIT_PER_MINUTE` based on expected usage patterns

### Logging Configuration

Controls application logging behavior.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | string | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_FILE` | string | `logs/nlp_server.log` | Path to log file |
| `LOG_ROTATION_DAYS` | integer | `30` | Days to keep log files |
| `LOG_FORMAT` | string | `json` | Log format (json or text) |

**Example:**
```env
LOG_LEVEL=INFO
LOG_FILE=logs/nlp_server.log
LOG_ROTATION_DAYS=30
LOG_FORMAT=json
```

**Log Levels:**
- `DEBUG`: Detailed information for debugging
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### Model Training Configuration

Hyperparameters for model training.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `BATCH_SIZE` | integer | `32` | Training batch size |
| `LEARNING_RATE` | float | `2e-5` | Learning rate for optimizer |
| `NUM_EPOCHS` | integer | `10` | Number of training epochs |
| `WARMUP_STEPS` | integer | `500` | Warmup steps for learning rate scheduler |
| `MAX_SEQ_LENGTH` | integer | `128` | Maximum sequence length for tokenization |

**Example:**
```env
BATCH_SIZE=32
LEARNING_RATE=2e-5
NUM_EPOCHS=10
WARMUP_STEPS=500
MAX_SEQ_LENGTH=128
```

**Tuning Tips:**
- Increase `BATCH_SIZE` if you have more GPU memory
- Decrease `LEARNING_RATE` if training is unstable
- Increase `NUM_EPOCHS` for better convergence (watch for overfitting)

### Data Augmentation Configuration

Controls data augmentation during training.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `AUGMENTATION_FACTOR` | integer | `2` | Number of augmented samples per original sample |
| `USE_PARAPHRASE` | boolean | `True` | Enable paraphrase generation |
| `USE_SYNONYM_REPLACEMENT` | boolean | `True` | Enable synonym replacement |
| `USE_TYPO_SIMULATION` | boolean | `True` | Enable typo simulation |

**Example:**
```env
AUGMENTATION_FACTOR=2
USE_PARAPHRASE=True
USE_SYNONYM_REPLACEMENT=True
USE_TYPO_SIMULATION=True
```

## Environment-Specific Configurations

### Development

```env
DEBUG=True
LOG_LEVEL=DEBUG
API_HOST=127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Production

```env
DEBUG=False
LOG_LEVEL=INFO
API_HOST=0.0.0.0
JWT_SECRET_KEY=<strong-secret-key>
CORS_ORIGINS=https://smarthome.example.com
DATABASE_URL=postgresql://nlp_user:secure_password@db.example.com:5432/nlp_production
REDIS_URL=redis://cache.example.com:6379/0
```

## Accessing Configuration in Code

```python
from src.config.settings import settings

# Access configuration values
print(f"API Version: {settings.api_version}")
print(f"Database URL: {settings.database_url}")
print(f"Model Path: {settings.model_path}")

# Get parsed CORS origins
origins = settings.get_cors_origins()
print(f"CORS Origins: {origins}")
```

## Validation

The configuration uses Pydantic for automatic validation:

- Type checking (string, integer, float, boolean)
- Default values for optional settings
- Environment variable loading
- Case-insensitive environment variable names

If configuration is invalid, the application will fail to start with a clear error message.

## Testing Configuration

Run the configuration tests:

```bash
pytest tests/unit/test_settings.py -v
```

This verifies:
- All required fields are present
- Default values are correct
- Types are validated
- CORS origins parsing works

## Security Best Practices

1. **Never commit `.env` to version control** - it's in `.gitignore`
2. **Use strong JWT secret keys** - minimum 32 characters
3. **Rotate secrets regularly** - especially in production
4. **Restrict CORS origins** - only allow trusted domains
5. **Use environment-specific configurations** - different settings for dev/staging/prod
6. **Secure database credentials** - use strong passwords and restrict access
7. **Enable HTTPS in production** - use reverse proxy (nginx, traefik)

## Troubleshooting

### Configuration not loading

1. Check that `.env` file exists in the `ai/` directory
2. Verify environment variable names match exactly (case-insensitive)
3. Check for syntax errors in `.env` file

### Invalid configuration values

1. Check the error message for which field is invalid
2. Verify the type matches (string, integer, float, boolean)
3. Ensure required fields are not empty

### CORS errors

1. Verify `CORS_ORIGINS` includes the requesting domain
2. Check that protocol (http/https) matches
3. Ensure no trailing slashes in origins

## Additional Resources

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI Configuration](https://fastapi.tiangolo.com/advanced/settings/)
- [12-Factor App Configuration](https://12factor.net/config)

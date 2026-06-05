# Quick Start Checklist ✅

Follow these steps to get the Vietnamese NLP Intent Classification Server up and running.

## Prerequisites Check

- [ ] Python 3.9+ installed (run `python --version`)
- [ ] pip installed (run `pip --version`)
- [ ] Git installed (optional, for version control)

## Setup Steps

### 1. Navigate to Project Directory
```bash
cd ai
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### 4. Upgrade pip
```bash
pip install --upgrade pip
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

⏱️ This may take 5-10 minutes depending on your internet connection.

### 6. Create Environment File
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### 7. Edit Environment File (Optional)
Open `.env` in your text editor and update:
- `JWT_SECRET_KEY` - Change to a secure random string
- `DATABASE_URL` - Update if using different database
- `REDIS_URL` - Update if using different Redis instance

### 8. Verify Installation
```bash
pytest tests/unit/test_sample.py -v
```

Expected output:
```
✅ tests/unit/test_sample.py::test_sample_addition PASSED
✅ tests/unit/test_sample.py::test_sample_string PASSED
✅ tests/unit/test_sample.py::test_sample_with_marker PASSED
```

### 9. Start Development Server

**Option A - Using script (Windows):**
```bash
run_dev.bat
```

**Option B - Using script (Linux/Mac):**
```bash
chmod +x run_dev.sh
./run_dev.sh
```

**Option C - Manual:**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### 10. Test the Server

Open your browser and visit:
- **API Root:** http://localhost:8001/
- **Health Check:** http://localhost:8001/health
- **API Docs:** http://localhost:8001/docs

You should see the API documentation interface.

## Verification Checklist

- [ ] Virtual environment created and activated
- [ ] All dependencies installed without errors
- [ ] Sample tests pass
- [ ] Development server starts without errors
- [ ] Can access http://localhost:8001/health
- [ ] Can access http://localhost:8001/docs

## Common Issues & Solutions

### Issue: `python` command not found
**Solution:** Try `python3` instead of `python`

### Issue: Permission denied on run_dev.sh
**Solution:** Run `chmod +x run_dev.sh` first

### Issue: Port 8001 already in use
**Solution:** Change port in command:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8002
```

### Issue: Import errors when running tests
**Solution:** Make sure virtual environment is activated and you're in the `ai/` directory

### Issue: PyTorch installation takes too long
**Solution:** Install CPU version first:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

## Next Steps

Once everything is working:

1. ✅ Read `README.md` for project overview
2. ✅ Read `SETUP.md` for detailed setup guide
3. ✅ Read `ENTITY_SCHEMA.md` for entity reference
4. ✅ Check `.kiro/specs/vietnamese-nlp-intent-classification/tasks.md` for next tasks
5. ✅ Start implementing Task 1.2 (Configuration Management)

## Docker Alternative

If you prefer Docker:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f nlp-server

# Stop services
docker-compose down
```

## Success! 🎉

If you've completed all steps and the server is running, you're ready to start development!

The basic infrastructure is now set up. You can proceed with implementing the NLP features according to the task list.

---

**Need Help?**
- Check `README.md` for detailed documentation
- Check `SETUP.md` for troubleshooting
- Check `PROJECT_STATUS.md` for what's been completed

# Aarohan Setu 2.0 - Placement Portal Startup Guide

Aarohan Setu 2.0 is a modern, premium campus placement cell management portal built with **Flask (Python)** on the backend and **Vue 3 (Single File Components via CDN)** on the frontend.

Follow this guide to set up and run the application on another machine.

---

## 📋 Prerequisites
1. **Python 3.10+**: Ensure Python is installed and added to the system PATH.
2. **Redis Server**: Required for background task execution (Celery) and analytics caching.

---


### 1. Unzip the Project Files
Extract the zip file to your desired project directory.

> [!WARNING]
> Do NOT copy the `venv/` folder if it is present in the zip file. Virtual environments contain absolute system paths and must be created fresh on each machine. If `venv/` is present, delete it before continuing.

### 2. Create and Activate a Virtual Environment
Open a terminal in the project root directory (`Aarohan_Setu_2.0/`) and run:

**On Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
With the virtual environment activated, install the required libraries:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Running the Application

### Option A: Automatic Orchestration (Recommended for Windows)
If you are on Windows, the project includes an orchestrator script `run.py` that automatically starts Redis, Celery Workers, Celery Beat, and the Flask API server together:
```bash
python run.py
```
*Note: The orchestrator will attempt to locate a local Redis installation automatically. If it cannot find it, ensure your Redis server is running manually in the background.*

### Option B: Manual Execution (All Operating Systems)
If you prefer running services in separate terminals, follow these steps with the virtual environment activated:

1. **Start Redis Server**:
   Make sure Redis is running on default port `6379`.

2. **Start Celery Background Worker**:
   ```bash
   # On Windows (use solo pool)
   celery -A backend.tasks.celery_app worker --loglevel=info -P solo

   # On macOS / Linux
   celery -A backend.tasks.celery_app worker --loglevel=info
   ```

3. **Start Celery Beat Scheduler (Optional - for daily alerts)**:
   ```bash
   celery -A backend.tasks.celery_app beat --loglevel=info
   ```

4. **Start Flask Web Server**:
   ```bash
   python -m backend.app
   ```

---

## 🖥️ Accessing the Portal
Once running, open your web browser and navigate to:
**[http://localhost:5001/](http://localhost:5001/)**

### Default Administrator Credentials:
- **Email**: `admin@aarohansetu.in`
- **Password**: `admin_password`

### Verification Test Suite
You can verify that everything is running correctly by running the tests:
```bash
python -m unittest test_app.py
python -m unittest test_background_jobs.py
```
=======
# Aarohan-Setu-2.0
It is a placement portal application.
>>>>>>> 5b8617daa4131f615c8b86261a76cae2a2fde211

# Local Installation & Setup Guide

## System Requirements
- **Operating System**: Windows 10/11, macOS 12+, or Ubuntu 20.04+
- **Python**: Version 3.10 to 3.12 (Python 3.12 recommended)
- **Git**: Installed and configured
- **Memory**: Minimum 4 GB RAM
- **Disk Space**: 500 MB free disk space

---

## Step-by-Step Installation

### 1. Clone the Repository
```bash
git clone git@github.com:rajeshwari229080/Datheon_AI_Automation_-_Agent_Building.git
cd Datheon_AI_Automation_-_Agent_Building/rw
```

### 2. Set Up Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the template configuration file:
```bash
# Windows PowerShell
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` in your text editor. By default, `DEMO_MODE=true` is enabled, allowing you to run all four modules, test suites, and the dashboard locally without requiring external cloud API keys.

To connect live services:
- Set `DEMO_MODE=false`
- Supply `OPENAI_API_KEY`, `AIRTABLE_API_KEY`, `SLACK_BOT_TOKEN`, `GOOGLE_SHEET_ID`, or `STRIPE_API_KEY` as needed.

### 5. Launch the Application Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## Verifying the Installation

1. Open your browser and navigate to:
   - Dashboard: `http://127.0.0.1:8000/`
   - API Docs: `http://127.0.0.1:8000/docs`
   - Health Check: `http://127.0.0.1:8000/api/v1/health`

2. Run the automated verification test suite:
   ```bash
   pytest tests/ -v
   ```
   All tests should pass.

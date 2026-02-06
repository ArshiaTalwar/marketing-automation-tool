# Marketing Automation Tool - Setup Guide

## ⚡ Quick Start (5 minutes)

### Step 1: Backend Setup

```bash
# Navigate to project directory
cd marketing-automation-tool

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start Backend Server

```bash
# Run FastAPI server
python app/main.py

# Server will start on http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Step 3: Frontend Setup (New Terminal)

```bash
# Navigate to dashboard folder
cd dashboard

# Install dependencies
npm install

# Start React development server
npm start

# Dashboard will open on http://localhost:3000
```

### Step 4: Test Upload

In a new terminal:

```bash
# Upload sample data
curl -X POST http://localhost:8000/upload-csv \
  -F "file=@data/sample_marketing.csv"
```

Expected response:
```json
{
  "status": "success",
  "message": "success",
  "rows_loaded": 21,
  "filename": "sample_marketing.csv"
}
```

## ✅ Verify Installation

### Check Backend
```bash
# Health check
curl http://localhost:8000/health

# Get summary
curl http://localhost:8000/summary

# Open API docs
open http://localhost:8000/docs
```

### Check Frontend
- Visit http://localhost:3000
- You should see the marketing dashboard

## 📊 Try the Dashboard

1. **Overview Tab** → See summary statistics
2. **Daily Performance Tab** → View trends over time
3. **Top Campaigns Tab** → Compare campaign performance
4. **Upload Logs Tab** → Check upload history

## 🧪 Run Tests

```bash
# Install test dependencies
pip install pytest pandas

# Run tests
pytest tests/ -v
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# FastAPI port 8000
# On macOS/Linux:
lsof -i :8000
kill -9 <PID>

# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Python Version
```bash
# Check Python version (should be 3.8+)
python --version
```

### Virtual Environment Issues
```bash
# Delete and recreate venv
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node Modules Issues
```bash
cd dashboard
rm -rf node_modules package-lock.json
npm install
npm start
```

## 📁 Project Files Explanation

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application entry point |
| `app/models.py` | SQLAlchemy ORM models (database schema) |
| `app/etl.py` | Pandas ETL pipeline logic |
| `app/routes.py` | FastAPI endpoint definitions |
| `dashboard/Dashboard.jsx` | React component with charts |
| `dashboard/Dashboard.css` | Styling for dashboard |
| `data/sample_marketing.csv` | Sample data for testing |
| `requirements.txt` | Python dependencies |
| `dashboard/package.json` | Node.js dependencies |

## 🚀 Next Steps

### For Testing
1. Upload the sample CSV: `data/sample_marketing.csv`
2. Check the dashboard at `http://localhost:3000`
3. Try different date ranges and filters

### For Development
1. Read `README.md` for API documentation
2. Explore `app/etl.py` to understand data processing
3. Modify `dashboard/Dashboard.jsx` to add new visualizations
4. Add custom metrics in `app/etl.py`

### For Production
1. Switch database to PostgreSQL
2. Add authentication (JWT)
3. Deploy with Docker
4. Set up CI/CD pipeline
5. Enable HTTPS and proper CORS

## 📞 Common Commands

```bash
# Start backend
python app/main.py

# Start frontend (from dashboard folder)
npm start

# Run tests
pytest tests/ -v

# Check API endpoints
curl http://localhost:8000/

# Get metrics
curl "http://localhost:8000/metrics?campaign=google"

# Get top campaigns
curl "http://localhost:8000/top-campaigns?limit=5&metric=spend"

# Health check
curl http://localhost:8000/health
```

## 💾 Database

Database file: `marketing_data.db` (SQLite)
- Auto-created on first run
- Located in project root
- Contains 3 tables: `raw_marketing_data`, `processed_metrics`, `upload_logs`

To reset database:
```bash
rm marketing_data.db
python app/main.py  # Will recreate tables
```

## 🎓 Learning Path

1. **Beginner**: Upload sample data, explore dashboard
2. **Intermediate**: Modify sample CSV, add custom columns
3. **Advanced**: Add new endpoints, integrate external APIs
4. **Expert**: Deploy to cloud, add authentication, scale database

---

**You're all set! 🎉 Start exploring the tool!**

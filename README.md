# Marketing Automation & Internal Dashboard Tool

An internal tool designed for marketing teams to automate data processing, metrics calculation, and reporting. Built with Python (FastAPI), SQL, Pandas, and React.

## 🎯 Problem Statement

Marketing teams typically:
- Download CSVs from ad platforms (Google Ads, Meta, etc.)
- Manually clean data in Excel
- Calculate metrics like CTR, CPC, ROI
- Create weekly reports (error-prone & time-consuming)

**This tool automates all of that.**

## ✨ Features

### Core Features (MVP)
- **CSV Upload API** - Upload marketing data with automatic validation
- **Automated Metrics Calculation** - Auto-compute CTR, CPC, ROI, etc.
- **REST APIs** - Clean endpoints for data retrieval
- **Real-time Dashboard** - Visual metrics and trend analysis
- **Upload History** - Track all CSV imports with detailed logs

### Metrics Calculated
- **CTR** = clicks / impressions × 100
- **CPC** = spend / clicks
- **ROI** = (revenue - spend) / spend × 100

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI |
| **Database** | SQLite (SQLAlchemy ORM) |
| **ETL** | Pandas, NumPy |
| **Frontend** | React, Recharts |
| **Server** | Uvicorn |

## 📁 Project Structure

```
marketing-automation-tool/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app & routes setup
│   ├── models.py               # SQLAlchemy models (ORM)
│   ├── etl.py                  # Pandas ETL pipeline
│   └── routes.py               # API endpoints
├── data/
│   └── sample_marketing.csv    # Sample data for testing
├── dashboard/
│   ├── Dashboard.jsx           # React component
│   ├── Dashboard.css           # Styling
│   └── package.json            # NPM dependencies
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── marketing_data.db           # SQLite database (auto-created)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+ (for React dashboard)
- pip & npm

### 1. Backend Setup

```bash
# Clone/navigate to project
cd marketing-automation-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start FastAPI Server

```bash
python app/main.py
```

Server runs on `http://localhost:8000`

**API Documentation**: Visit `http://localhost:8000/docs` (Swagger UI)

### 3. Frontend Setup

```bash
cd dashboard

# Install dependencies
npm install

# Start React dev server
npm start
```

Dashboard runs on `http://localhost:3000`

### 4. Test with Sample Data

Upload the sample CSV:
```bash
curl -X POST http://localhost:8000/upload-csv \
  -F "file=@data/sample_marketing.csv"
```

Response:
```json
{
  "status": "success",
  "message": "success",
  "rows_loaded": 21,
  "filename": "sample_marketing.csv"
}
```

## 📡 API Endpoints

### Upload Data
```http
POST /upload-csv
Content-Type: multipart/form-data

Expected CSV columns:
- date (YYYY-MM-DD)
- campaign_name
- impressions (integer)
- clicks (integer)
- spend (float)
- revenue (float, optional)
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/upload-csv \
  -F "file=@marketing_data.csv"
```

**Response:**
```json
{
  "status": "success",
  "rows_loaded": 50,
  "filename": "marketing_data.csv"
}
```

### Get Metrics
```http
GET /metrics?date_from=2026-01-01&date_to=2026-01-31&campaign=google
```

**Response:**
```json
{
  "data": [
    {
      "date": "2026-01-01",
      "campaign_name": "google search - q1",
      "impressions": 5000,
      "clicks": 150,
      "spend": 500.00,
      "revenue": 2500.00,
      "ctr": 3.0,
      "cpc": 3.33,
      "roi": 400.0
    }
  ],
  "count": 1
}
```

### Get Summary
```http
GET /summary
```

**Response:**
```json
{
  "total_spend": 15000.50,
  "total_revenue": 45000.00,
  "total_impressions": 125000,
  "total_clicks": 3750,
  "avg_ctr": 3.0,
  "avg_cpc": 4.00,
  "avg_roi": 200.0,
  "num_campaigns": 3,
  "total_records": 50
}
```

### Get Campaigns
```http
GET /campaigns
```

**Response:**
```json
{
  "campaigns": ["google search - q1", "meta ads - lead gen", "linkedin - b2b"],
  "count": 3
}
```

### Get Daily Performance
```http
GET /daily-performance
```

**Response:**
```json
{
  "data": [
    {
      "date": "2026-01-01",
      "spend": 1200.00,
      "revenue": 5500.00,
      "impressions": 10000,
      "clicks": 300,
      "campaigns": 3,
      "ctr": 3.0,
      "cpc": 4.0,
      "roi": 358.33
    }
  ],
  "count": 21
}
```

### Get Top Campaigns
```http
GET /top-campaigns?limit=5&metric=spend
```

**Supported metrics:** `spend`, `impressions`, `clicks`, `revenue`, `ctr`, `roi`

### Get Upload Logs
```http
GET /upload-logs?limit=10
```

### Health Check
```http
GET /health
```

## 📊 CSV Format

Create your CSV with these columns:

```csv
date,campaign_name,impressions,clicks,spend,revenue
2026-01-01,Google Search,5000,150,500,2500
2026-01-01,Meta Ads,3000,90,300,1800
2026-01-02,Google Search,5200,160,520,2800
```

### Required Columns
- `date` - Date in YYYY-MM-DD format
- `campaign_name` - Campaign identifier (string)
- `impressions` - Number of impressions (integer ≥ 0)
- `clicks` - Number of clicks (integer, ≤ impressions)
- `spend` - Spend amount (float ≥ 0)

### Optional Columns
- `revenue` - Revenue generated (float, defaults to 0)

### Validation Rules
✓ No duplicate rows  
✓ Clicks ≤ Impressions  
✓ No negative values  
✓ Valid date format  
✓ Proper data types  

## 🔄 ETL Pipeline

### Step 1: Validate
- Check required columns
- Validate data types
- Apply business logic rules

### Step 2: Clean
- Remove duplicates
- Handle missing values
- Standardize campaign names
- Format dates

### Step 3: Calculate Metrics
- CTR = clicks / impressions
- CPC = spend / clicks
- ROI = (revenue - spend) / spend

### Step 4: Load
- Store raw data in `raw_marketing_data` table
- Store processed metrics in `processed_metrics` table
- Log upload in `upload_logs` table

## 📈 Dashboard Features

### Overview Tab
- Summary statistics cards
- Total spend, revenue, impressions
- Average metrics (CTR, CPC, ROI)
- Top campaigns by spend

### Daily Performance Tab
- Spend & revenue trend line chart
- CTR & CPC trend analysis
- Time-series visualization

### Top Campaigns Tab
- Campaign metrics comparison table
- Sortable by all metrics
- Campaign performance details

### Upload Logs Tab
- Recent CSV uploads history
- Success/failure status
- Error messages (if any)

## 🎯 Usage Workflow

### For Marketing Teams

**Day 1: Weekly Review**
1. Download CSVs from Google Ads, Meta, LinkedIn
2. Click "Upload CSV" in dashboard
3. View auto-calculated metrics instantly
4. Check daily trends and top performers
5. Export/share summary report

**No manual Excel work needed!**

### For Developers

**Extend with Custom Metrics:**

Edit `app/etl.py`:
```python
# Add custom metric to MarketingETL.calculate_metrics()
df['custom_metric'] = df['spend'] / df['impressions'] * 1000
```

Then use the API:
```http
GET /metrics?campaign=google
```

## 🧪 Testing

### Unit Test ETL
```python
from app.etl import MarketingETL
import pandas as pd

# Test validation
df = pd.read_csv('data/sample_marketing.csv')
is_valid, msg = MarketingETL.validate_csv(df)
print(f"Valid: {is_valid}")
```

### Test API
```bash
# Health check
curl http://localhost:8000/health

# Get summary
curl http://localhost:8000/summary

# Get metrics for specific date
curl "http://localhost:8000/metrics?date_from=2026-01-01"
```

## 📝 Database Schema

### raw_marketing_data
```sql
id (PK)
campaign_name (indexed)
date (indexed)
impressions
clicks
spend
revenue
uploaded_at
```

### processed_metrics
```sql
id (PK)
campaign_name (indexed)
date (indexed)
impressions
clicks
spend
revenue
ctr
cpc
roi
calculated_at
```

### upload_logs
```sql
id (PK)
filename
rows_uploaded
status (success/failed/partial)
uploaded_at
error_message
```

## 🔐 Security Notes

**For internal use only.** Current version:
- No authentication (add if needed)
- No rate limiting (add for production)
- SQLite database (upgrade to PostgreSQL for production)
- CORS enabled for all origins (restrict as needed)

## 🚀 Production Deployment

### Upgrade Checklist

- [ ] Switch to PostgreSQL
- [ ] Add JWT authentication
- [ ] Enable rate limiting
- [ ] Restrict CORS to specific domains
- [ ] Add input sanitization
- [ ] Set up CI/CD pipeline
- [ ] Add comprehensive logging
- [ ] Enable database backups
- [ ] Use environment variables for config

### Deploy with Docker

```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ app/
CMD ["python", "app/main.py"]
```

## 📊 Resume-Ready Description

```
Marketing Automation Tool | Python, FastAPI, SQL, React

• Built an internal tool to automate marketing data processing and reporting
• Implemented ETL pipelines using Pandas to clean and transform CSV data
• Exposed REST APIs using FastAPI for metrics retrieval (CTR, CPC, ROI)
• Reduced manual reporting effort by automating repetitive workflows
• Designed responsive React dashboard with real-time metrics visualization
• Designed the solution for rapid iteration and internal stakeholder use
```

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pandas ETL Guide](https://pandas.pydata.org/docs/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [React Recharts](https://recharts.org/)

## 📞 Support

- 🐛 Report bugs via GitHub issues
- 💡 Suggest features
- 📧 Contact: [your-email]

## 📄 License

MIT License - Feel free to use for internal projects

---

**Built with ❤️ for marketing teams**


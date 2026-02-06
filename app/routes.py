from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
import tempfile
import os
from app.models import get_db, ProcessedMetrics, UploadLog, RawMarketingData
from app.etl import MarketingETL

router = APIRouter()


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and process marketing CSV file
    
    Expected columns: date, campaign_name, impressions, clicks, spend
    Optional: revenue (defaults to 0 if missing)
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Process CSV through ETL
        success, message, rows_loaded = MarketingETL.process_csv(
            tmp_path, db, file.filename
        )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        if success:
            return {
                "status": "success",
                "message": message,
                "rows_loaded": rows_loaded,
                "filename": file.filename
            }
        else:
            raise HTTPException(status_code=400, detail=message)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/metrics")
async def get_metrics(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    campaign: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get metrics with optional filtering
    
    Query params:
    - date_from: YYYY-MM-DD
    - date_to: YYYY-MM-DD
    - campaign: campaign name (partial match)
    """
    query = db.query(ProcessedMetrics)
    
    if date_from:
        query = query.filter(ProcessedMetrics.date >= date_from)
    if date_to:
        query = query.filter(ProcessedMetrics.date <= date_to)
    if campaign:
        query = query.filter(ProcessedMetrics.campaign_name.ilike(f"%{campaign}%"))
    
    metrics = query.order_by(ProcessedMetrics.date.desc()).all()
    
    if not metrics:
        return {"data": [], "count": 0}
    
    return {
        "data": [
            {
                "date": str(m.date),
                "campaign_name": m.campaign_name,
                "impressions": m.impressions,
                "clicks": m.clicks,
                "spend": m.spend,
                "revenue": m.revenue,
                "ctr": m.ctr,
                "cpc": m.cpc,
                "roi": m.roi
            }
            for m in metrics
        ],
        "count": len(metrics)
    }


@router.get("/summary")
async def get_summary(db: Session = Depends(get_db)):
    """Get high-level summary of all marketing data"""
    metrics = db.query(ProcessedMetrics).all()
    
    if not metrics:
        return {
            "total_spend": 0,
            "total_revenue": 0,
            "total_impressions": 0,
            "total_clicks": 0,
            "avg_ctr": 0,
            "avg_cpc": 0,
            "avg_roi": 0,
            "num_campaigns": 0,
            "total_records": 0
        }
    
    total_spend = sum(m.spend for m in metrics)
    total_revenue = sum(m.revenue for m in metrics)
    total_impressions = sum(m.impressions for m in metrics)
    total_clicks = sum(m.clicks for m in metrics)
    
    return {
        "total_spend": round(total_spend, 2),
        "total_revenue": round(total_revenue, 2),
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "avg_ctr": round(sum(m.ctr for m in metrics) / len(metrics), 2),
        "avg_cpc": round(sum(m.cpc for m in metrics) / len(metrics), 2),
        "avg_roi": round(sum(m.roi for m in metrics) / len(metrics), 2),
        "num_campaigns": len(set(m.campaign_name for m in metrics)),
        "total_records": len(metrics)
    }


@router.get("/campaigns")
async def get_campaigns(db: Session = Depends(get_db)):
    """Get all unique campaigns"""
    campaigns = db.query(ProcessedMetrics.campaign_name).distinct().all()
    return {
        "campaigns": [c[0] for c in campaigns],
        "count": len(campaigns)
    }


@router.get("/daily-performance")
async def get_daily_performance(db: Session = Depends(get_db)):
    """Get daily aggregated performance"""
    metrics = db.query(ProcessedMetrics).order_by(ProcessedMetrics.date).all()
    
    daily_data = {}
    for m in metrics:
        date_key = str(m.date)
        if date_key not in daily_data:
            daily_data[date_key] = {
                "date": date_key,
                "spend": 0,
                "revenue": 0,
                "impressions": 0,
                "clicks": 0,
                "campaigns": 0
            }
        
        daily_data[date_key]["spend"] += m.spend
        daily_data[date_key]["revenue"] += m.revenue
        daily_data[date_key]["impressions"] += m.impressions
        daily_data[date_key]["clicks"] += m.clicks
        daily_data[date_key]["campaigns"] = len(set(
            m.campaign_name for m in db.query(ProcessedMetrics)
            .filter(ProcessedMetrics.date == m.date).all()
        ))
    
    # Calculate aggregated metrics
    for date_key, data in daily_data.items():
        data["ctr"] = round(
            (data["clicks"] / data["impressions"] * 100) if data["impressions"] > 0 else 0, 2
        )
        data["cpc"] = round(
            (data["spend"] / data["clicks"]) if data["clicks"] > 0 else 0, 2
        )
        data["roi"] = round(
            ((data["revenue"] - data["spend"]) / data["spend"] * 100) if data["spend"] > 0 else 0, 2
        )
    
    return {
        "data": list(daily_data.values()),
        "count": len(daily_data)
    }


@router.get("/top-campaigns")
async def get_top_campaigns(limit: int = Query(5), metric: str = Query("spend"), db: Session = Depends(get_db)):
    """
    Get top campaigns by metric
    
    metric: spend, impressions, clicks, revenue, ctr, roi
    """
    valid_metrics = {"spend", "impressions", "clicks", "revenue", "ctr", "roi"}
    if metric not in valid_metrics:
        raise HTTPException(status_code=400, detail=f"Invalid metric. Must be one of: {valid_metrics}")
    
    metrics = db.query(ProcessedMetrics).all()
    
    # Aggregate by campaign
    campaign_data = {}
    for m in metrics:
        if m.campaign_name not in campaign_data:
            campaign_data[m.campaign_name] = {
                "campaign_name": m.campaign_name,
                "spend": 0,
                "revenue": 0,
                "impressions": 0,
                "clicks": 0,
                "records": 0
            }
        
        campaign_data[m.campaign_name]["spend"] += m.spend
        campaign_data[m.campaign_name]["revenue"] += m.revenue
        campaign_data[m.campaign_name]["impressions"] += m.impressions
        campaign_data[m.campaign_name]["clicks"] += m.clicks
        campaign_data[m.campaign_name]["records"] += 1
    
    # Calculate avg metrics
    for name, data in campaign_data.items():
        data["ctr"] = round(
            (data["clicks"] / data["impressions"] * 100) if data["impressions"] > 0 else 0, 2
        )
        data["roi"] = round(
            ((data["revenue"] - data["spend"]) / data["spend"] * 100) if data["spend"] > 0 else 0, 2
        )
    
    # Sort by requested metric
    if metric in {"ctr", "roi"}:
        sorted_campaigns = sorted(
            campaign_data.values(),
            key=lambda x: x[metric],
            reverse=True
        )
    else:
        sorted_campaigns = sorted(
            campaign_data.values(),
            key=lambda x: x[metric],
            reverse=True
        )
    
    return {
        "data": sorted_campaigns[:limit],
        "count": len(sorted_campaigns),
        "metric": metric
    }


@router.get("/upload-logs")
async def get_upload_logs(limit: int = Query(20), db: Session = Depends(get_db)):
    """Get recent upload logs"""
    logs = db.query(UploadLog).order_by(UploadLog.uploaded_at.desc()).limit(limit).all()
    
    return {
        "data": [
            {
                "filename": log.filename,
                "rows_uploaded": log.rows_uploaded,
                "status": log.status,
                "uploaded_at": str(log.uploaded_at),
                "error_message": log.error_message
            }
            for log in logs
        ],
        "count": len(logs)
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Marketing Automation Tool"
    }

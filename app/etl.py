import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models import RawMarketingData, ProcessedMetrics, UploadLog


class MarketingETL:
    """ETL pipeline for marketing data"""
    
    REQUIRED_COLUMNS = {"date", "campaign_name", "impressions", "clicks", "spend"}
    
    @staticmethod
    def validate_csv(df: pd.DataFrame) -> Tuple[bool, str]:
        """Validate CSV has required columns and data types"""
        # Check required columns
        missing_cols = MarketingETL.REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            return False, f"Missing columns: {missing_cols}"
        
        # Check for empty dataframe
        if df.empty:
            return False, "CSV file is empty"
        
        # Check data types
        try:
            df['date'] = pd.to_datetime(df['date'])
            df['impressions'] = pd.to_numeric(df['impressions'])
            df['clicks'] = pd.to_numeric(df['clicks'])
            df['spend'] = pd.to_numeric(df['spend'])
            df['campaign_name'] = df['campaign_name'].astype(str)
        except Exception as e:
            return False, f"Data type conversion error: {str(e)}"
        
        # Business logic validation
        if (df['clicks'] > df['impressions']).any():
            return False, "Clicks cannot exceed impressions"
        
        if (df['spend'] < 0).any() or (df['impressions'] < 0).any():
            return False, "Negative values not allowed"
        
        return True, "Validation passed"
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize data"""
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        df['revenue'] = df.get('revenue', 0).fillna(0)
        df['clicks'] = df['clicks'].fillna(0).astype(int)
        df['impressions'] = df['impressions'].fillna(0).astype(int)
        df['spend'] = df['spend'].fillna(0).astype(float)
        
        # Standardize date format
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        # Standardize campaign names
        df['campaign_name'] = df['campaign_name'].str.strip().str.lower()
        
        return df
    
    @staticmethod
    def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate CTR, CPC, ROI"""
        df = df.copy()
        
        # CTR = clicks / impressions (avoid division by zero)
        df['ctr'] = np.where(
            df['impressions'] > 0,
            (df['clicks'] / df['impressions'] * 100).round(2),
            0
        )
        
        # CPC = spend / clicks (avoid division by zero)
        df['cpc'] = np.where(
            df['clicks'] > 0,
            (df['spend'] / df['clicks']).round(2),
            0
        )
        
        # ROI = (revenue - spend) / spend * 100 (avoid division by zero)
        df['roi'] = np.where(
            df['spend'] > 0,
            ((df['revenue'] - df['spend']) / df['spend'] * 100).round(2),
            0
        )
        
        return df
    
    @staticmethod
    def load_to_database(df: pd.DataFrame, db: Session, filename: str) -> Tuple[int, str]:
        """Load processed data to database"""
        try:
            # Store raw data
            for _, row in df.iterrows():
                raw_record = RawMarketingData(
                    campaign_name=row['campaign_name'],
                    date=row['date'],
                    impressions=int(row['impressions']),
                    clicks=int(row['clicks']),
                    spend=float(row['spend']),
                    revenue=float(row['revenue'])
                )
                db.add(raw_record)
            
            # Store processed metrics
            for _, row in df.iterrows():
                metric_record = ProcessedMetrics(
                    campaign_name=row['campaign_name'],
                    date=row['date'],
                    impressions=int(row['impressions']),
                    clicks=int(row['clicks']),
                    spend=float(row['spend']),
                    revenue=float(row['revenue']),
                    ctr=float(row['ctr']),
                    cpc=float(row['cpc']),
                    roi=float(row['roi'])
                )
                db.add(metric_record)
            
            # Log upload
            upload_log = UploadLog(
                filename=filename,
                rows_uploaded=len(df),
                status="success"
            )
            db.add(upload_log)
            db.commit()
            
            return len(df), "success"
        
        except Exception as e:
            db.rollback()
            upload_log = UploadLog(
                filename=filename,
                rows_uploaded=0,
                status="failed",
                error_message=str(e)
            )
            db.add(upload_log)
            db.commit()
            return 0, f"Database error: {str(e)}"
    
    @staticmethod
    def process_csv(file_path: str, db: Session, filename: str) -> Tuple[bool, str, int]:
        """Full ETL pipeline"""
        try:
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Validate
            is_valid, validation_msg = MarketingETL.validate_csv(df)
            if not is_valid:
                log = UploadLog(
                    filename=filename,
                    rows_uploaded=0,
                    status="failed",
                    error_message=validation_msg
                )
                db.add(log)
                db.commit()
                return False, validation_msg, 0
            
            # Clean
            df = MarketingETL.clean_data(df)
            
            # Calculate metrics
            df = MarketingETL.calculate_metrics(df)
            
            # Load
            rows_loaded, status_msg = MarketingETL.load_to_database(df, db, filename)
            
            return True, status_msg, rows_loaded
        
        except Exception as e:
            log = UploadLog(
                filename=filename,
                rows_uploaded=0,
                status="failed",
                error_message=str(e)
            )
            db.add(log)
            db.commit()
            return False, str(e), 0

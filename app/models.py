from sqlalchemy import Column, Integer, String, Float, Date, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class RawMarketingData(Base):
    """Raw uploaded CSV data"""
    __tablename__ = "raw_marketing_data"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String, index=True)
    date = Column(Date, index=True)
    impressions = Column(Integer)
    clicks = Column(Integer)
    spend = Column(Float)
    revenue = Column(Float, nullable=True)  # Mock revenue
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class ProcessedMetrics(Base):
    """Calculated metrics from raw data"""
    __tablename__ = "processed_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String, index=True)
    date = Column(Date, index=True)
    impressions = Column(Integer)
    clicks = Column(Integer)
    spend = Column(Float)
    revenue = Column(Float)
    ctr = Column(Float)  # Click-through rate
    cpc = Column(Float)  # Cost per click
    roi = Column(Float)  # Return on investment
    calculated_at = Column(DateTime, default=datetime.utcnow)


class UploadLog(Base):
    """Track all CSV uploads"""
    __tablename__ = "upload_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    rows_uploaded = Column(Integer)
    status = Column(String)  # success, failed, partial
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(String, nullable=True)


# Database configuration
DATABASE_URL = "sqlite:///./marketing_data.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

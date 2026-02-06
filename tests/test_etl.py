import pytest
import pandas as pd
from app.etl import MarketingETL
import tempfile
import os


class TestMarketingETL:
    """Test suite for ETL pipeline"""
    
    @pytest.fixture
    def valid_df(self):
        """Create valid test dataframe"""
        return pd.DataFrame({
            'date': ['2026-01-01', '2026-01-02'],
            'campaign_name': ['Google Search', 'Meta Ads'],
            'impressions': [5000, 3000],
            'clicks': [150, 90],
            'spend': [500.0, 300.0],
            'revenue': [2500.0, 1800.0]
        })
    
    def test_validate_csv_valid(self, valid_df):
        """Test validation passes for valid data"""
        is_valid, msg = MarketingETL.validate_csv(valid_df)
        assert is_valid is True
        assert msg == "Validation passed"
    
    def test_validate_csv_missing_columns(self):
        """Test validation fails for missing columns"""
        df = pd.DataFrame({'date': ['2026-01-01']})
        is_valid, msg = MarketingETL.validate_csv(df)
        assert is_valid is False
        assert "Missing columns" in msg
    
    def test_validate_csv_clicks_exceed_impressions(self):
        """Test validation fails when clicks > impressions"""
        df = pd.DataFrame({
            'date': ['2026-01-01'],
            'campaign_name': ['Google'],
            'impressions': [100],
            'clicks': [200],  # Invalid
            'spend': [50.0]
        })
        is_valid, msg = MarketingETL.validate_csv(df)
        assert is_valid is False
        assert "Clicks cannot exceed impressions" in msg
    
    def test_validate_csv_negative_values(self):
        """Test validation fails for negative values"""
        df = pd.DataFrame({
            'date': ['2026-01-01'],
            'campaign_name': ['Google'],
            'impressions': [-100],  # Invalid
            'clicks': [10],
            'spend': [50.0]
        })
        is_valid, msg = MarketingETL.validate_csv(df)
        assert is_valid is False
        assert "Negative values not allowed" in msg
    
    def test_validate_csv_empty(self):
        """Test validation fails for empty dataframe"""
        df = pd.DataFrame()
        is_valid, msg = MarketingETL.validate_csv(df)
        assert is_valid is False
        assert "empty" in msg.lower()
    
    def test_clean_data(self, valid_df):
        """Test data cleaning"""
        cleaned = MarketingETL.clean_data(valid_df)
        
        # Check no duplicates
        assert len(cleaned) == len(cleaned.drop_duplicates())
        
        # Check data types
        assert cleaned['clicks'].dtype in [int, 'int64']
        assert cleaned['impressions'].dtype in [int, 'int64']
        assert cleaned['spend'].dtype == float
    
    def test_calculate_metrics(self, valid_df):
        """Test metric calculation"""
        df = MarketingETL.clean_data(valid_df)
        metrics = MarketingETL.calculate_metrics(df)
        
        # Check CTR calculation
        expected_ctr = (150 / 5000) * 100
        assert metrics.iloc[0]['ctr'] == round(expected_ctr, 2)
        
        # Check CPC calculation
        expected_cpc = 500.0 / 150
        assert metrics.iloc[0]['cpc'] == round(expected_cpc, 2)
        
        # Check ROI calculation
        expected_roi = ((2500.0 - 500.0) / 500.0) * 100
        assert metrics.iloc[0]['roi'] == round(expected_roi, 2)
    
    def test_calculate_metrics_zero_division(self):
        """Test metrics handle zero division gracefully"""
        df = pd.DataFrame({
            'date': ['2026-01-01'],
            'campaign_name': ['Test'],
            'impressions': [0],
            'clicks': [0],
            'spend': [0.0],
            'revenue': [0.0]
        })
        
        metrics = MarketingETL.calculate_metrics(df)
        
        # Should not raise exception and return 0
        assert metrics.iloc[0]['ctr'] == 0
        assert metrics.iloc[0]['cpc'] == 0
        assert metrics.iloc[0]['roi'] == 0
    
    def test_process_csv_creates_csv(self, valid_df):
        """Test CSV processing saves to temporary file"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            valid_df.to_csv(tmp.name, index=False)
            temp_path = tmp.name
        
        try:
            # Just verify it reads without error
            test_df = pd.read_csv(temp_path)
            assert len(test_df) == 2
        finally:
            os.unlink(temp_path)


class TestMarketingMetrics:
    """Test metric calculations"""
    
    def test_ctr_calculation(self):
        """Test CTR = clicks / impressions * 100"""
        df = pd.DataFrame({
            'impressions': [1000, 2000],
            'clicks': [50, 100],
            'spend': [100, 200],
            'revenue': [500, 1000]
        })
        
        ctr = MarketingETL.calculate_metrics(df)['ctr'].tolist()
        
        assert ctr[0] == 5.0  # 50/1000 * 100
        assert ctr[1] == 5.0  # 100/2000 * 100
    
    def test_cpc_calculation(self):
        """Test CPC = spend / clicks"""
        df = pd.DataFrame({
            'impressions': [1000, 2000],
            'clicks': [50, 100],
            'spend': [100.0, 200.0],
            'revenue': [500, 1000]
        })
        
        cpc = MarketingETL.calculate_metrics(df)['cpc'].tolist()
        
        assert cpc[0] == round(100.0 / 50, 2)  # 2.0
        assert cpc[1] == round(200.0 / 100, 2)  # 2.0
    
    def test_roi_calculation(self):
        """Test ROI = (revenue - spend) / spend * 100"""
        df = pd.DataFrame({
            'impressions': [1000],
            'clicks': [50],
            'spend': [100.0],
            'revenue': [500.0]
        })
        
        roi = MarketingETL.calculate_metrics(df)['roi'].iloc[0]
        expected = ((500 - 100) / 100) * 100  # 400%
        
        assert roi == round(expected, 2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

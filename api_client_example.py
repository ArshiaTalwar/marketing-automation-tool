"""
Example API Client for Marketing Automation Tool

Demonstrates how to interact with the API programmatically
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json

BASE_URL = "http://localhost:8000"


class MarketingAPIClient:
    """Client for Marketing Automation Tool API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def upload_csv(self, csv_file_path: str) -> dict:
        """Upload marketing CSV file"""
        with open(csv_file_path, 'rb') as f:
            files = {'file': f}
            response = self.session.post(
                f"{self.base_url}/upload-csv",
                files=files
            )
        return response.json()
    
    def get_summary(self) -> dict:
        """Get high-level summary of all data"""
        response = self.session.get(f"{self.base_url}/summary")
        return response.json()
    
    def get_metrics(
        self,
        date_from: str = None,
        date_to: str = None,
        campaign: str = None
    ) -> dict:
        """Get metrics with optional filtering"""
        params = {}
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        if campaign:
            params['campaign'] = campaign
        
        response = self.session.get(
            f"{self.base_url}/metrics",
            params=params
        )
        return response.json()
    
    def get_campaigns(self) -> dict:
        """Get all unique campaigns"""
        response = self.session.get(f"{self.base_url}/campaigns")
        return response.json()
    
    def get_daily_performance(self) -> dict:
        """Get daily aggregated performance"""
        response = self.session.get(f"{self.base_url}/daily-performance")
        return response.json()
    
    def get_top_campaigns(
        self,
        limit: int = 5,
        metric: str = "spend"
    ) -> dict:
        """Get top campaigns by specified metric"""
        params = {
            'limit': limit,
            'metric': metric
        }
        response = self.session.get(
            f"{self.base_url}/top-campaigns",
            params=params
        )
        return response.json()
    
    def get_upload_logs(self, limit: int = 10) -> dict:
        """Get recent upload logs"""
        params = {'limit': limit}
        response = self.session.get(
            f"{self.base_url}/upload-logs",
            params=params
        )
        return response.json()
    
    def health_check(self) -> dict:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def example_usage():
    """Example usage of the API client"""
    
    # Initialize client
    client = MarketingAPIClient()
    
    # Health check
    print_section("1. Health Check")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    # Upload sample data
    print_section("2. Upload CSV Data")
    try:
        upload_result = client.upload_csv("data/sample_marketing.csv")
        print(json.dumps(upload_result, indent=2))
    except FileNotFoundError:
        print("Sample CSV not found. Skipping upload.")
    
    # Get summary
    print_section("3. Get Summary Statistics")
    summary = client.get_summary()
    print(json.dumps(summary, indent=2))
    
    # Get campaigns
    print_section("4. Get All Campaigns")
    campaigns = client.get_campaigns()
    print(json.dumps(campaigns, indent=2))
    
    # Get top campaigns
    print_section("5. Top Campaigns by Spend")
    top_campaigns = client.get_top_campaigns(limit=3, metric="spend")
    if top_campaigns['count'] > 0:
        for campaign in top_campaigns['data']:
            print(f"\n  Campaign: {campaign['campaign_name']}")
            print(f"  Spend: ${campaign['spend']:.2f}")
            print(f"  Revenue: ${campaign['revenue']:.2f}")
            print(f"  CTR: {campaign['ctr']:.2f}%")
            print(f"  ROI: {campaign['roi']:.1f}%")
    else:
        print("  No campaign data available")
    
    # Get top campaigns by ROI
    print_section("6. Top Campaigns by ROI")
    top_roi = client.get_top_campaigns(limit=3, metric="roi")
    if top_roi['count'] > 0:
        for campaign in top_roi['data']:
            print(f"\n  Campaign: {campaign['campaign_name']}")
            print(f"  ROI: {campaign['roi']:.1f}%")
            print(f"  CTR: {campaign['ctr']:.2f}%")
    else:
        print("  No campaign data available")
    
    # Get daily performance
    print_section("7. Daily Performance (Last 5 Days)")
    daily = client.get_daily_performance()
    if daily['count'] > 0:
        for day in daily['data'][-5:]:  # Last 5 days
            print(f"\n  Date: {day['date']}")
            print(f"  Spend: ${day['spend']:.2f}")
            print(f"  Revenue: ${day['revenue']:.2f}")
            print(f"  CTR: {day['ctr']:.2f}%")
            print(f"  CPC: ${day['cpc']:.2f}")
    else:
        print("  No daily data available")
    
    # Get metrics for specific date range
    print_section("8. Metrics for Date Range")
    metrics = client.get_metrics(
        date_from="2026-01-01",
        date_to="2026-01-07"
    )
    print(f"  Records found: {metrics['count']}")
    if metrics['count'] > 0:
        print(f"  First record: {metrics['data'][0]}")
    
    # Get metrics for specific campaign
    print_section("9. Metrics for Specific Campaign")
    campaign_metrics = client.get_metrics(campaign="google")
    print(f"  Campaign metrics found: {campaign_metrics['count']}")
    if campaign_metrics['count'] > 0:
        print(f"  Sample: {campaign_metrics['data'][0]}")
    
    # Get upload logs
    print_section("10. Recent Upload Logs")
    logs = client.get_upload_logs(limit=5)
    for log in logs['data']:
        print(f"\n  File: {log['filename']}")
        print(f"  Status: {log['status']}")
        print(f"  Rows: {log['rows_uploaded']}")
        print(f"  Uploaded: {log['uploaded_at']}")
    
    print_section("Examples Complete!")


def create_sample_data():
    """Create additional sample data for testing"""
    data = {
        'date': pd.date_range('2026-01-01', periods=30).strftime('%Y-%m-%d'),
        'campaign_name': ['Google Search'] * 10 + ['Meta Ads'] * 10 + ['LinkedIn'] * 10,
        'impressions': [5000 + i*100 for i in range(30)],
        'clicks': [150 + i*3 for i in range(30)],
        'spend': [500 + i*10 for i in range(30)],
        'revenue': [2500 + i*50 for i in range(30)]
    }
    
    df = pd.DataFrame(data)
    df.to_csv('data/extended_marketing.csv', index=False)
    print("✓ Created extended_marketing.csv")


if __name__ == "__main__":
    print("Marketing Automation Tool - API Client Examples")
    print(f"API Base URL: {BASE_URL}")
    
    # Run examples
    example_usage()
    
    # Optional: Create extended sample data
    print("\n\nWould you like to create extended sample data? (uncomment line below)")
    # create_sample_data()

import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import './Dashboard.css';

const API_BASE = 'http://localhost:8000';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [dailyData, setDailyData] = useState([]);
  const [topCampaigns, setTopCampaigns] = useState([]);
  const [uploadLogs, setUploadLogs] = useState([]);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [summaryRes, dailyRes, campaignsRes, logsRes] = await Promise.all([
        fetch(`${API_BASE}/summary`),
        fetch(`${API_BASE}/daily-performance`),
        fetch(`${API_BASE}/top-campaigns?limit=5&metric=spend`),
        fetch(`${API_BASE}/upload-logs?limit=10`)
      ]);

      if (summaryRes.ok) setSummary(await summaryRes.json());
      if (dailyRes.ok) setDailyData((await dailyRes.json()).data);
      if (campaignsRes.ok) setTopCampaigns((await campaignsRes.json()).data);
      if (logsRes.ok) setUploadLogs((await logsRes.json()).data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploadStatus('Uploading...');
      const response = await fetch(`${API_BASE}/upload-csv`, {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (response.ok) {
        setUploadStatus(`✓ Success! Loaded ${result.rows_loaded} rows`);
        setUploadFile(null);
        setTimeout(() => {
          fetchData();
          setUploadStatus('');
        }, 1000);
      } else {
        setUploadStatus(`✗ Error: ${result.detail}`);
      }
    } catch (error) {
      setUploadStatus(`✗ Upload failed: ${error.message}`);
    }
  };

  const StatCard = ({ label, value, subtext, icon }) => (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <p className="stat-label">{label}</p>
        <p className="stat-value">{value}</p>
        {subtext && <p className="stat-subtext">{subtext}</p>}
      </div>
    </div>
  );

  if (loading && !summary) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1>📊 Marketing Automation Dashboard</h1>
          <p>Real-time marketing metrics & performance tracking</p>
        </div>
        <div className="header-actions">
          <label className="upload-button">
            📁 Upload CSV
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </label>
          <button className="refresh-button" onClick={fetchData}>
            🔄 Refresh
          </button>
        </div>
      </header>

      {uploadStatus && (
        <div className={`upload-status ${uploadStatus.includes('Success') ? 'success' : 'error'}`}>
          {uploadStatus}
        </div>
      )}

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveTab('performance')}
        >
          Daily Performance
        </button>
        <button
          className={`tab ${activeTab === 'campaigns' ? 'active' : ''}`}
          onClick={() => setActiveTab('campaigns')}
        >
          Top Campaigns
        </button>
        <button
          className={`tab ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          Upload Logs
        </button>
      </div>

      <div className="dashboard-content">
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <>
            {/* Summary Stats */}
            {summary && (
              <div className="stats-grid">
                <StatCard
                  label="Total Spend"
                  value={`$${summary.total_spend?.toLocaleString()}`}
                  subtext={`${summary.total_records} records`}
                  icon="💰"
                />
                <StatCard
                  label="Total Revenue"
                  value={`$${summary.total_revenue?.toLocaleString()}`}
                  subtext={`${summary.num_campaigns} campaigns`}
                  icon="💵"
                />
                <StatCard
                  label="Avg CTR"
                  value={`${summary.avg_ctr}%`}
                  subtext="Click-through rate"
                  icon="📈"
                />
                <StatCard
                  label="Avg CPC"
                  value={`$${summary.avg_cpc?.toFixed(2)}`}
                  subtext="Cost per click"
                  icon="💳"
                />
                <StatCard
                  label="Avg ROI"
                  value={`${summary.avg_roi?.toFixed(1)}%`}
                  subtext="Return on investment"
                  icon="🎯"
                />
                <StatCard
                  label="Total Impressions"
                  value={summary.total_impressions?.toLocaleString()}
                  subtext={`${summary.total_clicks} clicks`}
                  icon="👁️"
                />
              </div>
            )}

            {/* Top Campaigns */}
            {topCampaigns.length > 0 && (
              <div className="chart-container">
                <h2>Top Campaigns by Spend</h2>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={topCampaigns}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="campaign_name" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                    <Legend />
                    <Bar dataKey="spend" fill="#3b82f6" name="Spend" />
                    <Bar dataKey="revenue" fill="#10b981" name="Revenue" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </>
        )}

        {/* DAILY PERFORMANCE TAB */}
        {activeTab === 'performance' && dailyData.length > 0 && (
          <>
            <div className="chart-container">
              <h2>Daily Spend & Revenue Trend</h2>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                  <Legend />
                  <Line type="monotone" dataKey="spend" stroke="#3b82f6" name="Spend" strokeWidth={2} />
                  <Line type="monotone" dataKey="revenue" stroke="#10b981" name="Revenue" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-container">
              <h2>Daily CTR & CPC Trend</h2>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" label={{ value: 'CTR (%)', angle: -90, position: 'insideLeft' }} />
                  <YAxis yAxisId="right" orientation="right" label={{ value: 'CPC ($)', angle: 90, position: 'insideRight' }} />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="ctr" stroke="#f59e0b" name="CTR (%)" strokeWidth={2} />
                  <Line yAxisId="right" type="monotone" dataKey="cpc" stroke="#ef4444" name="CPC ($)" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </>
        )}

        {/* CAMPAIGNS TAB */}
        {activeTab === 'campaigns' && topCampaigns.length > 0 && (
          <>
            <div className="chart-container">
              <h2>Campaign Metrics Comparison</h2>
              <div className="table-container">
                <table className="metrics-table">
                  <thead>
                    <tr>
                      <th>Campaign</th>
                      <th>Spend</th>
                      <th>Revenue</th>
                      <th>Impressions</th>
                      <th>Clicks</th>
                      <th>CTR (%)</th>
                      <th>ROI (%)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topCampaigns.map((campaign, idx) => (
                      <tr key={idx}>
                        <td className="campaign-name">{campaign.campaign_name}</td>
                        <td className="number">${campaign.spend.toFixed(2)}</td>
                        <td className="number">${campaign.revenue.toFixed(2)}</td>
                        <td className="number">{campaign.impressions.toLocaleString()}</td>
                        <td className="number">{campaign.clicks.toLocaleString()}</td>
                        <td className="number">{campaign.ctr.toFixed(2)}%</td>
                        <td className={`number ${campaign.roi >= 0 ? 'positive' : 'negative'}`}>
                          {campaign.roi.toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* LOGS TAB */}
        {activeTab === 'logs' && uploadLogs.length > 0 && (
          <div className="chart-container">
            <h2>Upload History</h2>
            <div className="table-container">
              <table className="logs-table">
                <thead>
                  <tr>
                    <th>Filename</th>
                    <th>Rows</th>
                    <th>Status</th>
                    <th>Uploaded</th>
                    <th>Message</th>
                  </tr>
                </thead>
                <tbody>
                  {uploadLogs.map((log, idx) => (
                    <tr key={idx}>
                      <td>{log.filename}</td>
                      <td>{log.rows_uploaded}</td>
                      <td>
                        <span className={`status ${log.status}`}>
                          {log.status === 'success' ? '✓' : '✗'} {log.status}
                        </span>
                      </td>
                      <td>{new Date(log.uploaded_at).toLocaleString()}</td>
                      <td>{log.error_message || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;

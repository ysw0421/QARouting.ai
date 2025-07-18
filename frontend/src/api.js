// Centralized API utility for report management
const API_BASE = 'http://localhost:8000/api';

function getToken() {
  return localStorage.getItem('token');
}

export async function saveReport(report) {
  const res = await fetch(`${API_BASE}/reports`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`,
    },
    body: JSON.stringify(report),
  });
  if (!res.ok) throw new Error('Failed to save report');
  return await res.json();
}

export async function listReports() {
  const res = await fetch(`${API_BASE}/reports`, {
    headers: {
      'Authorization': `Bearer ${getToken()}`,
    },
  });
  if (!res.ok) throw new Error('Failed to list reports');
  return await res.json();
}

export async function loadReport(reportId) {
  const res = await fetch(`${API_BASE}/reports/${reportId}`, {
    headers: {
      'Authorization': `Bearer ${getToken()}`,
    },
  });
  if (!res.ok) throw new Error('Failed to load report');
  return await res.json();
} 
const API_BASE = 'http://127.0.0.1:5000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('jwt_token');
  return token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
};

export const fetchSecurityStats = async () => {
  const res = await fetch(`${API_BASE}/security/stats`, { headers: getAuthHeaders() });
  return await res.json();
};

export const fetchTrafficChart = async () => {
  const res = await fetch(`${API_BASE}/security/traffic-chart`, { headers: getAuthHeaders() });
  return await res.json();
};

export const fetchTrafficLogs = async (page = 1) => {
  const res = await fetch(`${API_BASE}/security/logs?page=${page}&per_page=30`, { headers: getAuthHeaders() });
  return await res.json();
};

export const fetchSecurityEvents = async () => {
  const res = await fetch(`${API_BASE}/security/events`, { headers: getAuthHeaders() });
  return await res.json();
};

export const fetchBlockedIps = async () => {
  const res = await fetch(`${API_BASE}/security/blocked-ips`, { headers: getAuthHeaders() });
  return await res.json();
};

export const unblockIpAddress = async (ipAddress) => {
  const res = await fetch(`${API_BASE}/security/unblock-ip`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ ip_address: ipAddress })
  });
  return await res.json();
};

export const blockIpAddressManual = async (ipAddress, reason) => {
  const res = await fetch(`${API_BASE}/security/block-ip`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ ip_address: ipAddress, reason, duration_minutes: 30 })
  });
  return await res.json();
};

export const resetSecurityData = async () => {
  const res = await fetch(`${API_BASE}/security/reset`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  return await res.json();
};

export const loginAdmin = async (username, password) => {
  const res = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return await res.json();
};

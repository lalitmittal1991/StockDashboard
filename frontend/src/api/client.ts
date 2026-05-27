const API_BASE = '/api';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function login(username: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(err.detail || 'Login failed');
  }
  return res.json();
}

export async function fetchDashboard(spreadsheetId: string, stocksRange?: string) {
  const res = await fetch(`${API_BASE}/dashboard/fetch`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      spreadsheet_id: spreadsheetId,
      stocks_range: stocksRange || 'Stocks!A2:B',
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Fetch failed' }));
    throw new Error(err.detail || 'Fetch failed');
  }
  return res.json();
}

export async function getSampleSheetFormat() {
  const res = await fetch(`${API_BASE}/dashboard/sample-sheet-format`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch sample format');
  return res.json();
}

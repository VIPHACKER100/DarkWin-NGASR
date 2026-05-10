/**
 * DARKWIN API Client
 * 
 * Provides utility functions for interacting with the DARKWIN Flask backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1';

export interface Scan {
  id: string;
  target: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at: string;
}

export interface Finding {
  type: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | 'Info';
  endpoint: string;
  description?: string;
}

export interface ScanDetail extends Scan {
  findings: Finding[];
}

export async function fetchScans(): Promise<Scan[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/scans`);
    if (!response.ok) throw new Error('Failed to fetch scans');
    return await response.json();
  } catch (error) {
    console.error('Error fetching scans:', error);
    return [];
  }
}

export async function fetchScanDetail(scanId: string): Promise<ScanDetail | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/scans/${scanId}`);
    if (!response.ok) throw new Error(`Failed to fetch scan detail for ${scanId}`);
    return await response.json();
  } catch (error) {
    console.error(`Error fetching scan detail for ${scanId}:`, error);
    return null;
  }
}

export async function initiateScan(target: string, pipeline: string = 'recon'): Promise<{ scan_id: string } | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/scans`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ target, pipeline }),
    });
    if (!response.ok) throw new Error('Failed to initiate scan');
    return await response.json();
  } catch (error) {
    console.error('Error initiating scan:', error);
    return null;
  }
}

export interface DashboardStats {
  total_targets: number;
  total_findings: number;
  critical_findings: number;
  active_scans: number;
  recent_findings: any[];
}

export async function fetchStats(): Promise<DashboardStats | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/stats`);
    if (!response.ok) throw new Error('Failed to fetch stats');
    return await response.json();
  } catch (error) {
    console.error('Error fetching stats:', error);
    return null;
  }
}

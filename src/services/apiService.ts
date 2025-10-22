/**
 * Central API service for the Queue Management System
 * Handles all HTTP requests to the backend API
 */

// Read Vite env var VITE_API_URL if provided, and normalize to have no trailing slash
const _VITE_API = (import.meta as any).env?.VITE_API_URL as string | undefined;
const _DEFAULT_API = 'http://127.0.0.1:8000';
// Ensure base does NOT include a trailing slash and does not end with '/api'
const API_BASE_URL = (_VITE_API && _VITE_API.length > 0 ? _VITE_API : _DEFAULT_API).replace(/\/+$/, '').replace(/\/api$/i, '');

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
  // Build URL safely: if endpoint starts with '/', append directly; otherwise prefix with '/'
  let url = endpoint.startsWith('/') ? `${this.baseUrl}${endpoint}` : `${this.baseUrl}/${endpoint}`;
  // Normalize accidental duplicate '/api/api' that can happen if both base and endpoint include '/api'
  url = url.replace(/\/api\/api\/+/g, '/api/').replace(/\/api\/api$/g, '/api');

  // Debug log to help trace final URL used for requests
  console.log(`apiService: Fetching ${url}`);
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // GET request
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  // POST request
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // PUT request
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // DELETE request
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  // PATCH request
  async patch<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export types for common API responses
export interface User {
  id: number;
  name: string;
  email: string;
  phone: string;
  date_of_birth: string;
}

export interface Service {
  id: number;
  name: string;
  description: string;
  department: string;
  staff_count: number;
  service_rate: number;
  estimated_time: number;
  current_wait_time: number;
  queue_length: number;
}

export interface QueueEntry {
  id: number;
  patient_id: number;
  service_id: number;
  queue_number: number;
  status: 'waiting' | 'called' | 'serving' | 'completed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  created_at: string;
  completed_at?: string;
  estimated_wait_time: number;
  ai_predicted_wait: number;
  patient?: User;
  service?: Service;
}

export interface ServiceCounter {
  id: number;
  name: string;
  service_id: number;
  is_active: boolean;
  current_queue_entry_id?: number;
  staff_member?: string;
}

export interface Analytics {
  id: number;
  timestamp: string;
  service_id: number;
  queue_length: number;
  avg_wait_time: number;
  avg_service_time: number;
  efficiency_score: number;
  peak_hour: number;
  peak_load: number;
  staff_utilization: number;
  patient_satisfaction: number;
  patients_served: number;
}

export interface AIRecommendation {
  type: 'critical' | 'warning' | 'improvement' | 'info';
  message: string;
  action: string;
}

export interface AIServiceSuggestion {
  service: string;
  confidence: number;
  urgency: 'low' | 'medium' | 'high';
  reasoning: string;
  alternative_services: string[];
  estimated_wait?: number;
}

export interface AIEfficiencyMetrics {
  efficiency_score: number;
  current_queue_length: number;
  avg_wait_time: number;
  staff_count: number;
  staff_utilization: number;
  throughput_per_hour: number;
  capacity_utilization: number;
  service_rate: number;
  recommendations: string[];
}

export interface AIStaffOptimization {
  service_id: number;
  service_name: string;
  current_staff: number;
  recommended_staff: number;
  efficiency_score: number;
  reasoning: string;
}

export interface EmergencyDispatch {
  id: number;
  patient_id: number;
  emergency_details: string;
  dispatch_address: string;
  dispatch_status: 'pending' | 'dispatched' | 'en_route' | 'arrived' | 'completed' | 'cancelled';
  dispatched_at?: string;
  response_time?: number;
  ambulance_id?: string;
  notes?: string;
  created_at: string;
  patient_name?: string;
  patient?: User;
}

export interface DispatchRequest {
  patient_id: number;
  emergency_details: string;
}

export interface DispatchStatusResponse extends EmergencyDispatch {
  patient_name?: string;
}

export default apiService;
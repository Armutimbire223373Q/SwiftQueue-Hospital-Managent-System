import AsyncStorage from '@react-native-async-storage/async-storage';
import { Alert } from 'react-native';

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

class ApiService {
  private baseURL: string;
  private token: string | null = null;

  constructor() {
    // In production, this should come from environment variables
    this.baseURL = 'http://localhost:8000'; // Change to your backend URL
    this.loadToken();
  }

  // Load token from storage
  private async loadToken(): Promise<void> {
    try {
      this.token = await AsyncStorage.getItem('authToken');
    } catch (error) {
      console.error('Error loading token:', error);
    }
  }

  // Save token to storage
  private async saveToken(token: string): Promise<void> {
    try {
      this.token = token;
      await AsyncStorage.setItem('authToken', token);
    } catch (error) {
      console.error('Error saving token:', error);
    }
  }

  // Remove token
  async logout(): Promise<void> {
    try {
      this.token = null;
      await AsyncStorage.removeItem('authToken');
    } catch (error) {
      console.error('Error removing token:', error);
    }
  }

  // Set base URL (useful for different environments)
  setBaseURL(url: string): void {
    this.baseURL = url;
  }

  // Get auth headers
  private getHeaders(includeAuth = true): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (includeAuth && this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // Handle API response
  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    try {
      const data = await response.json();

      if (response.ok) {
        return {
          success: true,
          data: data,
        };
      } else {
        // Handle authentication errors
        if (response.status === 401) {
          await this.logout();
          Alert.alert('Session Expired', 'Please log in again.');
        }

        return {
          success: false,
          error: data.detail || data.message || `HTTP ${response.status}`,
        };
      }
    } catch (error) {
      console.error('Response parsing error:', error);
      return {
        success: false,
        error: 'Network error or invalid response',
      };
    }
  }

  // GET request
  async get<T = any>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      console.error('GET request failed:', error);
      return {
        success: false,
        error: 'Network request failed',
      };
    }
  }

  // POST request
  async post<T = any>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: data ? JSON.stringify(data) : undefined,
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      console.error('POST request failed:', error);
      return {
        success: false,
        error: 'Network request failed',
      };
    }
  }

  // PUT request
  async put<T = any>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: data ? JSON.stringify(data) : undefined,
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      console.error('PUT request failed:', error);
      return {
        success: false,
        error: 'Network request failed',
      };
    }
  }

  // DELETE request
  async delete<T = any>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      console.error('DELETE request failed:', error);
      return {
        success: false,
        error: 'Network request failed',
      };
    }
  }

  // Authentication methods
  async login(email: string, password: string): Promise<ApiResponse> {
    const response = await this.post('/api/auth/login', { email, password });

    if (response.success && response.data?.access_token) {
      await this.saveToken(response.data.access_token);
    }

    return response;
  }

  async register(userData: {
    name: string;
    email: string;
    password: string;
    phone?: string;
    role?: string;
  }): Promise<ApiResponse> {
    return this.post('/api/auth/register', userData);
  }

  // Queue methods
  async joinQueue(queueData: {
    service_id: number;
    priority: string;
    symptoms?: string;
  }): Promise<ApiResponse> {
    return this.post('/api/queue/join', queueData);
  }

  async getQueueStatus(queueNumber: number): Promise<ApiResponse> {
    return this.get(`/api/queue/status/${queueNumber}`);
  }

  // Emergency methods
  async triggerSOS(emergencyData: any): Promise<ApiResponse> {
    return this.post('/api/emergency/sos', emergencyData);
  }

  // Appointment methods
  async getAppointments(): Promise<ApiResponse> {
    return this.get('/api/appointments/');
  }

  async bookAppointment(appointmentData: any): Promise<ApiResponse> {
    return this.post('/api/appointments/', appointmentData);
  }

  // Check network connectivity
  async checkConnectivity(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${this.baseURL}/health`, {
        method: 'GET',
        headers: this.getHeaders(false),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  // Get current token
  getToken(): string | null {
    return this.token;
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return this.token !== null;
  }
}

export const apiService = new ApiService();
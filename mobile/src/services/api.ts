import axios, { AxiosInstance, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ApiResponse, User, Service, QueueEntry, Appointment, LoginCredentials, RegisterData, QueueJoinData, AppointmentBookingData } from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL = 'http://localhost:8000/api'; // Update this for production

  constructor() {
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, clear storage
          await AsyncStorage.removeItem('authToken');
          await AsyncStorage.removeItem('userData');
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(credentials: LoginCredentials): Promise<ApiResponse<{ user: User; token: string }>> {
    try {
      const response: AxiosResponse = await this.api.post('/auth/login', credentials);
      const { user, access_token } = response.data;

      // Store token and user data
      await AsyncStorage.setItem('authToken', access_token);
      await AsyncStorage.setItem('userData', JSON.stringify(user));

      return { success: true, data: { user, token: access_token } };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      };
    }
  }

  async register(data: RegisterData): Promise<ApiResponse<User>> {
    try {
      const response: AxiosResponse = await this.api.post('/auth/register', data);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed'
      };
    }
  }

  async logout(): Promise<void> {
    await AsyncStorage.removeItem('authToken');
    await AsyncStorage.removeItem('userData');
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const userData = await AsyncStorage.getItem('userData');
      return userData ? JSON.parse(userData) : null;
    } catch {
      return null;
    }
  }

  // Services
  async getServices(): Promise<ApiResponse<Service[]>> {
    try {
      const response: AxiosResponse = await this.api.get('/services/');
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to load services'
      };
    }
  }

  // Queue Management
  async joinQueue(data: QueueJoinData): Promise<ApiResponse<QueueEntry>> {
    try {
      const response: AxiosResponse = await this.api.post('/queue/join', data);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to join queue'
      };
    }
  }

  async getQueueStatus(queueId: number): Promise<ApiResponse<QueueEntry>> {
    try {
      const response: AxiosResponse = await this.api.get(`/queue/status/${queueId}`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to get queue status'
      };
    }
  }

  async getUserQueues(): Promise<ApiResponse<QueueEntry[]>> {
    try {
      const response: AxiosResponse = await this.api.get('/users/queue-history');
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to load queue history'
      };
    }
  }

  async leaveQueue(queueId: number): Promise<ApiResponse<void>> {
    try {
      await this.api.delete(`/queue/${queueId}`);
      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to leave queue'
      };
    }
  }

  // Appointments
  async getAppointments(): Promise<ApiResponse<Appointment[]>> {
    try {
      const response: AxiosResponse = await this.api.get('/appointments/');
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to load appointments'
      };
    }
  }

  async bookAppointment(data: AppointmentBookingData): Promise<ApiResponse<Appointment>> {
    try {
      const response: AxiosResponse = await this.api.post('/appointments/', data);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to book appointment'
      };
    }
  }

  async cancelAppointment(appointmentId: number): Promise<ApiResponse<void>> {
    try {
      await this.api.delete(`/appointments/${appointmentId}`);
      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to cancel appointment'
      };
    }
  }

  // Emergency Services
  async requestEmergencyAssistance(data: { location: string; emergency_type: string }): Promise<ApiResponse<any>> {
    try {
      const response: AxiosResponse = await this.api.post('/emergency/assistance', data);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to request assistance'
      };
    }
  }

  // Navigation
  async getNavigationRoute(data: { from: string; to: string }): Promise<ApiResponse<any>> {
    try {
      const response: AxiosResponse = await this.api.post('/navigation/route', data);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to get route'
      };
    }
  }

  // Notifications
  async getNotifications(): Promise<ApiResponse<any[]>> {
    try {
      const response: AxiosResponse = await this.api.get('/notifications/');
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to load notifications'
      };
    }
  }

  async markNotificationRead(notificationId: number): Promise<ApiResponse<void>> {
    try {
      await this.api.put(`/notifications/${notificationId}/read`);
      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to mark notification as read'
      };
    }
  }
}

export const apiService = new ApiService();
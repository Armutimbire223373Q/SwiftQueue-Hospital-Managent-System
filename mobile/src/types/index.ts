// Mobile App Types for Healthcare Queue Management System

export interface User {
  id: number;
  name: string;
  email: string;
  role: 'patient' | 'staff' | 'admin';
  phone?: string;
  date_of_birth?: string;
}

export interface Service {
  id: number;
  name: string;
  department: string;
  description: string;
  estimated_wait_time: number;
  is_active: boolean;
}

export interface QueueEntry {
  id: number;
  queue_number: string;
  patient_id: number;
  patient_name: string;
  service_id: number;
  service_name: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  status: 'waiting' | 'called' | 'serving' | 'completed' | 'cancelled';
  position: number;
  estimated_wait_time: number;
  joined_at: string;
  called_at?: string;
}

export interface Appointment {
  id: number;
  patient_id: number;
  service_id: number;
  staff_id?: number;
  appointment_date: string;
  appointment_time: string;
  status: 'scheduled' | 'confirmed' | 'checked_in' | 'completed' | 'cancelled';
  notes?: string;
  created_at: string;
}

export interface NotificationData {
  id: number;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'success' | 'error';
  is_read: boolean;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  phone?: string;
  date_of_birth?: string;
}

export interface QueueJoinData {
  service_id: number;
  symptoms: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  patient_details: {
    name: string;
    phone: string;
    email: string;
    date_of_birth?: string;
  };
}

export interface AppointmentBookingData {
  service_id: number;
  appointment_date: string;
  appointment_time: string;
  notes?: string;
}

// Navigation Types
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  QueueJoin: { serviceId?: number };
  QueueStatus: { queueId: number };
  AppointmentBooking: undefined;
  AppointmentDetails: { appointmentId: number };
  Profile: undefined;
  Settings: undefined;
};

export type MainTabParamList = {
  Home: undefined;
  Queue: undefined;
  Appointments: undefined;
  Profile: undefined;
};

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
};
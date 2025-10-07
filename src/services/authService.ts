import apiClient from './apiClient';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  name: string;
  email: string;
  password: string;
  phone?: string;
  role?: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  refresh_token?: string;
  expires_in?: number;
}

interface User {
  id: number;
  name: string;
  email: string;
  phone?: string;
  role: string;
  is_active: boolean;
}

class AuthService {

  async login(email: string, password: string): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    const authData = response.data;

    // Store refresh token if provided
    if (authData.refresh_token) {
      localStorage.setItem('refresh_token', authData.refresh_token);
    }

    // Store token expiration time
    if (authData.expires_in) {
      const expirationTime = Date.now() + (authData.expires_in * 1000);
      localStorage.setItem('token_expires_at', expirationTime.toString());
    }

    return authData;
  }

  async register(userData: RegisterData): Promise<User> {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/auth/me');
    return response.data;
  }

  async updateProfile(updates: { name?: string; phone?: string }): Promise<void> {
    await apiClient.put('/auth/me', updates);
  }

  async getAllUsers(): Promise<User[]> {
    const response = await apiClient.get('/auth/users');
    return response.data;
  }

  async updateUserRole(userId: number, role: string): Promise<void> {
    await apiClient.put(`/auth/users/${userId}/role`, { role });
  }

  async updateUserStatus(userId: number, isActive: boolean): Promise<void> {
    await apiClient.put(`/auth/users/${userId}/status`, { is_active: isActive });
  }

  async refreshToken(): Promise<AuthResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiClient.post('/auth/refresh', {
      refresh_token: refreshToken,
    });

    const authData = response.data;

    // Update stored tokens
    if (authData.access_token) {
      localStorage.setItem('token', authData.access_token);
    }

    if (authData.refresh_token) {
      localStorage.setItem('refresh_token', authData.refresh_token);
    }

    if (authData.expires_in) {
      const expirationTime = Date.now() + (authData.expires_in * 1000);
      localStorage.setItem('token_expires_at', expirationTime.toString());
    }

    return authData;
  }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_expires_at');
    localStorage.removeItem('user');
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }

  getCurrentUserFromStorage(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  isTokenExpired(): boolean {
    const expirationTime = localStorage.getItem('token_expires_at');
    if (!expirationTime) return false;

    return Date.now() >= parseInt(expirationTime);
  }

  isTokenExpiringSoon(): boolean {
    const expirationTime = localStorage.getItem('token_expires_at');
    if (!expirationTime) return false;

    // Consider token expiring soon if it expires within 5 minutes
    const fiveMinutesFromNow = Date.now() + (5 * 60 * 1000);
    return parseInt(expirationTime) <= fiveMinutesFromNow;
  }
}

export const authService = new AuthService();
export type { User, LoginCredentials, RegisterData, AuthResponse };
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

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
  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async register(userData: RegisterData): Promise<User> {
    const response = await axios.post(`${API_BASE_URL}/auth/register`, userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await axios.get(`${API_BASE_URL}/auth/me`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async updateProfile(updates: { name?: string; phone?: string }): Promise<void> {
    await axios.put(`${API_BASE_URL}/auth/me`, updates, {
      headers: this.getAuthHeaders(),
    });
  }

  async getAllUsers(): Promise<User[]> {
    const response = await axios.get(`${API_BASE_URL}/auth/users`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async updateUserRole(userId: number, role: string): Promise<void> {
    await axios.put(
      `${API_BASE_URL}/auth/users/${userId}/role`,
      { role },
      { headers: this.getAuthHeaders() }
    );
  }

  async updateUserStatus(userId: number, isActive: boolean): Promise<void> {
    await axios.put(
      `${API_BASE_URL}/auth/users/${userId}/status`,
      { is_active: isActive },
      { headers: this.getAuthHeaders() }
    );
  }

  logout(): void {
    localStorage.removeItem('token');
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
}

export const authService = new AuthService();
export type { User, LoginCredentials, RegisterData, AuthResponse };
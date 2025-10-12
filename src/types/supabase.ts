export interface User {
  id: number;
  name: string;
  email: string;
  phone?: string;
  street_address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  role: string;
  is_active: boolean;
}

export interface UserCreate {
  name: string;
  email: string;
  password: string;
  phone?: string;
  street_address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  role?: string;
}

export interface UserResponse {
  id: number;
  name: string;
  email: string;
  phone?: string;
  street_address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  role: string;
  is_active: boolean;
}
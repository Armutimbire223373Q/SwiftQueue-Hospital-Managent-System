/**
 * Application constants and configuration
 */

export const APP_CONFIG = {
  name: 'SwiftQueue Hospital',
  version: '1.0.0',
  description: 'AI-Powered Hospital Queue Management System',
  apiBaseUrl: 'http://localhost:8000/api',
  wsBaseUrl: 'ws://localhost:8000/ws',
  refreshInterval: 30000, // 30 seconds
  notificationTimeout: 5000, // 5 seconds
} as const;

export const QUEUE_STATUS = {
  WAITING: 'waiting',
  CALLED: 'called',
  SERVING: 'serving',
  COMPLETED: 'completed',
} as const;

export const PRIORITY_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  URGENT: 'urgent',
} as const;

export const NOTIFICATION_TYPES = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  SUCCESS: 'success',
} as const;

export const DEPARTMENTS = {
  EMERGENCY: 'Emergency',
  CARDIOLOGY: 'Cardiology',
  GENERAL: 'General Medicine',
  LABORATORY: 'Laboratory',
  RADIOLOGY: 'Radiology',
  PEDIATRICS: 'Pediatrics',
} as const;

export const DEPARTMENT_ICONS = {
  [DEPARTMENTS.EMERGENCY]: 'AlertTriangle',
  [DEPARTMENTS.CARDIOLOGY]: 'Heart',
  [DEPARTMENTS.GENERAL]: 'Stethoscope',
  [DEPARTMENTS.LABORATORY]: 'Activity',
  [DEPARTMENTS.RADIOLOGY]: 'Monitor',
  [DEPARTMENTS.PEDIATRICS]: 'Users',
} as const;

export const WAIT_TIME_THRESHOLDS = {
  EXCELLENT: 10, // minutes
  GOOD: 20,
  FAIR: 30,
  POOR: 45,
} as const;

export const EFFICIENCY_SCORES = {
  EXCELLENT: 0.9,
  GOOD: 0.8,
  FAIR: 0.7,
  POOR: 0.6,
} as const;

export const AI_FEATURES = {
  PREDICTION_ACCURACY: 0.85,
  CONFIDENCE_THRESHOLD: 0.7,
  UPDATE_INTERVAL: 300000, // 5 minutes
  TRAINING_INTERVAL: 3600000, // 1 hour
} as const;

export const ROUTES = {
  HOME: '/',
  DASHBOARD: '/dashboard',
  QUEUE: '/queue',
  ADMIN: '/admin',
  ANALYTICS: '/analytics',
} as const;

export const API_ENDPOINTS = {
  QUEUE: {
    JOIN: '/queue/join',
    STATUS: '/queue/status',
    ALL: '/queue',
    SERVICE: '/queue/service',
    UPDATE_STATUS: '/queue',
    CALL_NEXT: '/queue/call-next',
  },
  SERVICES: {
    ALL: '/services',
    BY_ID: '/services',
    COUNTERS: '/services',
  },
  USERS: {
    ALL: '/users',
    BY_ID: '/users',
    BY_EMAIL: '/users/email',
    CREATE: '/users',
    UPDATE: '/users',
    DELETE: '/users',
    QUEUE_HISTORY: '/users',
    ACTIVE_QUEUES: '/users',
  },
  ANALYTICS: {
    WAIT_TIMES: '/analytics/wait-times',
    PEAK_HOURS: '/analytics/peak-hours',
    SERVICE_DISTRIBUTION: '/analytics/service-distribution',
    RECOMMENDATIONS: '/analytics/recommendations',
  },
  AI: {
    TRAIN: '/ai/train',
    WAIT_PREDICTION: '/ai/wait-prediction',
    ANOMALIES: '/ai/anomalies',
    SERVICE_SUGGESTION: '/ai/service-suggestion',
    EFFICIENCY: '/ai/efficiency',
    OPTIMIZE_STAFF: '/ai/optimize-staff',
  },
} as const;

export const WEBSOCKET_ENDPOINTS = {
  DASHBOARD: '/ws/dashboard',
  PATIENT: '/ws/patient',
} as const;

export const VALIDATION_RULES = {
  NAME: {
    MIN_LENGTH: 2,
    MAX_LENGTH: 50,
    PATTERN: /^[a-zA-Z\s]+$/,
  },
  EMAIL: {
    PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  PHONE: {
    PATTERN: /^[\+]?[1-9][\d]{0,15}$/,
  },
  SYMPTOMS: {
    MAX_LENGTH: 500,
  },
} as const;

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  NOT_FOUND: 'The requested resource was not found.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  FORBIDDEN: 'Access to this resource is forbidden.',
  RATE_LIMITED: 'Too many requests. Please try again later.',
} as const;

export const SUCCESS_MESSAGES = {
  QUEUE_JOINED: 'Successfully joined the queue!',
  STATUS_UPDATED: 'Status updated successfully.',
  DATA_SAVED: 'Data saved successfully.',
  OPERATION_COMPLETED: 'Operation completed successfully.',
} as const;

export const THEME_COLORS = {
  PRIMARY: 'blue',
  SECONDARY: 'gray',
  SUCCESS: 'green',
  WARNING: 'yellow',
  ERROR: 'red',
  INFO: 'blue',
} as const;

export const CHART_COLORS = [
  '#3B82F6', // blue
  '#10B981', // green
  '#F59E0B', // yellow
  '#EF4444', // red
  '#8B5CF6', // purple
  '#06B6D4', // cyan
  '#F97316', // orange
  '#84CC16', // lime
] as const;

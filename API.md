# SwiftQueue Hospital API Documentation

## Overview

The SwiftQueue Hospital API provides endpoints for managing hospital queues, patient registration, AI-powered predictions, and real-time analytics.

## Base URL

- Development: `http://localhost:8000/api`
- Production: `https://yourdomain.com/api`

## Authentication

Currently, the API does not require authentication. In production, implement JWT-based authentication.

## Endpoints

### Queue Management

#### Join Queue
```http
POST /api/queue/join
```

**Request Body:**
```json
{
  "service_id": 1,
  "patient_details": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "dateOfBirth": "1990-01-01",
    "symptoms": "Chest pain",
    "priority": "high"
  }
}
```

**Response:**
```json
{
  "queue_number": 123,
  "estimated_wait": 25,
  "ai_predicted_wait": 18
}
```

#### Get Queue Status
```http
GET /api/queue/status/{queue_number}
```

**Response:**
```json
{
  "status": "waiting",
  "position": 3,
  "estimated_wait": 18
}
```

#### Get All Queues
```http
GET /api/queue/
```

#### Get Service Queue
```http
GET /api/queue/service/{service_id}
```

#### Update Queue Status
```http
PUT /api/queue/{queue_id}/status
```

**Request Body:**
```json
{
  "status": "serving"
}
```

#### Call Next Patient
```http
POST /api/queue/call-next
```

**Request Body:**
```json
{
  "service_id": 1,
  "counter_id": 1
}
```

### Services

#### Get All Services
```http
GET /api/services/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Emergency Care",
    "description": "24/7 emergency medical services",
    "department": "Emergency",
    "staff_count": 3,
    "service_rate": 2.5,
    "estimated_time": 15,
    "current_wait_time": 20,
    "queue_length": 5
  }
]
```

#### Get Service by ID
```http
GET /api/services/{service_id}
```

#### Get Service Counters
```http
GET /api/services/{service_id}/counters
```

### Users

#### Create User
```http
POST /api/users/
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-01"
}
```

#### Get All Users
```http
GET /api/users/
```

#### Get User by ID
```http
GET /api/users/{user_id}
```

#### Update User
```http
PUT /api/users/{user_id}
```

#### Delete User
```http
DELETE /api/users/{user_id}
```

#### Get User Queue History
```http
GET /api/users/{user_id}/queue-history
```

#### Get User Active Queues
```http
GET /api/users/{user_id}/active-queues
```

### Analytics

#### Get Wait Times
```http
GET /api/analytics/wait-times
```

**Response:**
```json
[
  {
    "date": "2024-01-15",
    "avgWait": 18.5
  }
]
```

#### Get Peak Hours
```http
GET /api/analytics/peak-hours
```

**Response:**
```json
[
  {
    "hour": 14,
    "count": 25
  }
]
```

#### Get Service Distribution
```http
GET /api/analytics/service-distribution
```

**Response:**
```json
[
  {
    "serviceId": 1,
    "count": 45
  }
]
```

#### Get AI Recommendations
```http
GET /api/analytics/recommendations
```

**Response:**
```json
[
  {
    "type": "warning",
    "message": "High wait times for Emergency Care",
    "action": "Consider activating additional counters for Emergency Care"
  }
]
```

### AI Features

#### Train AI Models
```http
POST /api/ai/train
```

**Response:**
```json
{
  "message": "AI models successfully trained"
}
```

#### Get Wait Time Prediction
```http
GET /api/ai/wait-prediction/{service_id}
```

**Response:**
```json
{
  "service_id": 1,
  "service_name": "Emergency Care",
  "predicted_wait_minutes": 18.5
}
```

#### Detect Anomalies
```http
GET /api/ai/anomalies
```

**Response:**
```json
{
  "anomalies_detected": 2,
  "anomalies": [
    {
      "service_id": 1,
      "metrics": {
        "queue_length": 15,
        "wait_time": 45.2,
        "staff_count": 2,
        "service_rate": 1.8
      },
      "severity": "high"
    }
  ]
}
```

#### Get Service Suggestion
```http
POST /api/ai/service-suggestion
```

**Request Body:**
```json
{
  "symptoms": "chest pain, shortness of breath"
}
```

**Response:**
```json
{
  "service": "Emergency Care",
  "confidence": 0.85,
  "urgency": "high",
  "reasoning": "Based on symptoms analysis, Emergency Care is recommended",
  "alternative_services": ["Cardiology"],
  "estimated_wait": 15.5
}
```

#### Get Service Efficiency
```http
GET /api/ai/efficiency/{service_id}
```

**Response:**
```json
{
  "service_id": 1,
  "service_name": "Emergency Care",
  "metrics": {
    "efficiency_score": 0.85,
    "current_queue_length": 8,
    "avg_wait_time": 22.5,
    "staff_count": 3,
    "staff_utilization": 0.78,
    "throughput_per_hour": 7.5,
    "capacity_utilization": 0.65,
    "service_rate": 2.5,
    "recommendations": [
      "Service operating within normal parameters"
    ]
  }
}
```

#### Get Staff Optimization
```http
GET /api/ai/optimize-staff
```

**Response:**
```json
{
  "recommendations": [
    {
      "service_id": 1,
      "service_name": "Emergency Care",
      "current_staff": 3,
      "recommended_staff": 4,
      "efficiency_score": 0.85,
      "reasoning": "Queue length: 12, Avg wait time: 25.5 min, Efficiency score: 0.85"
    }
  ],
  "total_adjustments_needed": 1
}
```

## WebSocket Endpoints

### Dashboard Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/dashboard');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Dashboard update:', data);
};
```

### Patient Notifications
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/patient/123');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Patient notification:', data);
};
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

Error responses include a `detail` field with the error message:

```json
{
  "detail": "Service not found"
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse. Current limits:

- General endpoints: 100 requests per minute
- AI endpoints: 20 requests per minute
- WebSocket connections: 10 per IP

## CORS

The API supports CORS for the following origins:

- `http://localhost:5173` (Development)
- `http://127.0.0.1:5173` (Development)
- Production domains (configured via environment variables)

## Data Models

### Queue Entry
```typescript
interface QueueEntry {
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
```

### Service
```typescript
interface Service {
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
```

### User
```typescript
interface User {
  id: number;
  name: string;
  email: string;
  phone: string;
  date_of_birth: string;
}
```

## Testing

Run the test suite:

```bash
cd backend
python -m pytest test_main.py -v
```

## Support

For API support and questions:

- Check the API documentation at `http://localhost:8000/docs` when running
- Create an issue in the GitHub repository
- Review the source code in the `backend/app/routes/` directory

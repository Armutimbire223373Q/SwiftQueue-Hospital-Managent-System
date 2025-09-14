# SwiftQueue Hospital - AI-Powered Queue Management System

A comprehensive hospital queue management system with AI-powered predictions, real-time monitoring, and intelligent resource optimization.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Automated Setup
```bash
# Run the setup script
python setup.py
```

### Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd queue-management-system
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   python init_db.py
   ```

3. **Frontend Setup**
   ```bash
   # From project root
   npm install
   ```

4. **Start the Application**
   ```bash
   # From project root
   cd backend
   python run.py
   ```

   This will start both the backend API (port 8000) and frontend (port 5173).

### Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🏥 Features

### Core Functionality
- **Patient Registration**: Digital queue joining with priority-based scheduling
- **Real-time Dashboard**: Live monitoring of all hospital departments
- **AI Predictions**: Smart wait time estimation and patient flow forecasting
- **Staff Management**: Resource allocation and workload optimization
- **Analytics**: Comprehensive reporting and performance insights
- **Engaging Splash Screen**: Professional loading experience with animated branding
- **Modern Home Page**: Beautiful landing page with live statistics and department information
- **Interactive Navigation**: Smart navigation with notifications and department quick access

### AI-Powered Features
- **Intelligent Wait Time Prediction**: ML-based estimation using historical patterns
- **Service Recommendation**: AI suggests appropriate department based on symptoms
- **Anomaly Detection**: Automatic identification of system irregularities
- **Staff Optimization**: AI recommendations for optimal staffing levels
- **Peak Time Prediction**: Forecasting busy periods for better preparation

### Real-time Features
- **WebSocket Integration**: Live updates for dashboards and patient notifications
- **Instant Notifications**: Real-time alerts for patients and staff
- **Live Queue Status**: Dynamic queue position and wait time updates

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd queue-management-system
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   # From project root
   npm install
   ```

4. **Initialize Database**
   ```bash
   cd backend
   python init_db.py
   ```

5. **Start the Application**
   ```bash
   # From project root
   cd backend
   python run.py
   ```

   This will start both the backend API (port 8000) and frontend (port 5173).

### Alternative: Start Services Separately

**Backend only:**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend only:**
```bash
npm run dev
```

## 📁 Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── ai/             # AI models and utilities
│   │   │   ├── models.py   # ML models (RandomForest, IsolationForest)
│   │   │   ├── predictors.py # Queue prediction logic
│   │   │   └── utils.py    # AI utility functions
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   │   ├── ai.py       # AI-powered endpoints
│   │   │   ├── analytics.py # Analytics and reporting
│   │   │   ├── queue.py    # Queue management
│   │   │   ├── services.py # Hospital services
│   │   │   └── users.py    # User management
│   │   ├── database.py     # Database configuration
│   │   ├── main.py         # FastAPI application
│   │   └── ws.py           # WebSocket handlers
│   ├── init_db.py          # Database initialization
│   └── run.py              # Application runner
├── src/                    # React frontend
│   ├── components/         # React components
│   │   ├── admin-panel.tsx # Admin management interface
���   │   ├── customer-queue.tsx # Patient queue interface
│   │   ├── home.tsx        # Landing page
│   │   └── queue-dashboard.tsx # Staff dashboard
│   ├── services/           # API services
│   │   ├── aiService.ts    # AI feature integration
│   │   ├── apiService.ts   # Core API client
│   │   ├── analyticsService.ts # Analytics data
│   │   ├── queueService.ts # Queue operations
│   │   └── wsService.ts    # WebSocket client
│   └── lib/                # Utilities and configurations
└── README.md
```

## 🔧 API Endpoints

### Queue Management
- `POST /api/queue/join` - Join a queue
- `GET /api/queue/status/{queue_number}` - Get queue status

### Services
- `GET /api/services/` - List all services
- `GET /api/services/{service_id}` - Get service details
- `GET /api/services/{service_id}/counters` - Get service counters

### AI Features
- `POST /api/ai/train` - Train AI models
- `GET /api/ai/wait-prediction/{service_id}` - Predict wait times
- `GET /api/ai/anomalies` - Detect system anomalies
- `POST /api/ai/service-suggestion` - Get service recommendations
- `GET /api/ai/efficiency/{service_id}` - Get efficiency metrics
- `GET /api/ai/optimize-staff` - Get staff optimization recommendations

### Analytics
- `GET /api/analytics/wait-times` - Wait time analytics
- `GET /api/analytics/peak-hours` - Peak hour analysis
- `GET /api/analytics/service-distribution` - Service usage distribution
- `GET /api/analytics/recommendations` - System recommendations

### Users
- `POST /api/users/` - Create user
- `GET /api/users/` - List users
- `GET /api/users/{user_id}` - Get user details
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user

### WebSocket Endpoints
- `ws://localhost:8000/ws/dashboard` - Dashboard real-time updates
- `ws://localhost:8000/ws/patient/{queue_number}` - Patient notifications

## 🤖 AI Models

### Queue Predictor
- **Algorithm**: Random Forest Regressor
- **Features**: Hour of day, day of week, queue length, staff count, service ID
- **Purpose**: Predict accurate wait times for patients

### Anomaly Detector
- **Algorithm**: Isolation Forest
- **Features**: Queue length, wait time, staff count, service rate
- **Purpose**: Identify unusual system behavior and potential issues

### Service Recommendation
- **Method**: Keyword matching with medical knowledge base
- **Input**: Patient symptoms (text)
- **Output**: Recommended department with confidence score

## 🏥 Hospital Departments

The system supports multiple hospital departments:

- **Emergency Care**: 24/7 emergency medical services
- **General Medicine**: Primary care and consultations
- **Cardiology**: Heart and cardiovascular care
- **Laboratory Services**: Blood tests and diagnostics
- **Radiology**: Medical imaging and scans
- **Pediatrics**: Child and infant care

## 📊 Dashboard Features

### Patient Interface
- Service selection and queue joining
- Real-time wait time updates
- Queue position tracking
- Notification system

### Staff Dashboard
- Live queue monitoring
- Patient management
- Service counter control
- AI-powered insights

### Admin Panel
- Staff management
- Service area configuration
- System analytics
- AI model training
- Resource optimization

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Environment
ENV=development

# CORS Settings
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Production Settings (when ENV=production)
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Database
DATABASE_URL=sqlite:///./queue_management.db
```

### AI Model Configuration

AI models are automatically trained with sample data during initialization. To retrain models:

```bash
curl -X POST http://localhost:8000/api/ai/train
```

## 🚀 Deployment

### Production Deployment

1. **Set environment variables**:
   ```env
   ENV=production
   ALLOWED_ORIGINS=https://yourdomain.com
   ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
   ```

2. **Build frontend**:
   ```bash
   npm run build
   ```

3. **Start backend**:
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.9

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
COPY frontend/dist ./static

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
npm test
```

### API Testing
Use the provided Postman collection or test with curl:

```bash
# Join queue
curl -X POST http://localhost:8000/api/queue/join \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": 1,
    "patient_details": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "dateOfBirth": "1990-01-01",
      "priority": "medium"
    }
  }'

# Get queue status
curl http://localhost:8000/api/queue/status/1

# Get AI prediction
curl http://localhost:8000/api/ai/wait-prediction/1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue in the GitHub repository
- Check the documentation in the `/docs` folder
- Review the API documentation at `http://localhost:8000/docs` when running

## 🔮 Future Enhancements

- **Mobile App**: React Native mobile application
- **Advanced AI**: Deep learning models for better predictions
- **Integration**: Hospital management system integration
- **Multi-language**: Internationalization support
- **Voice Notifications**: Audio alerts and announcements
- **Biometric Integration**: Fingerprint/face recognition for patient identification
- **Telemedicine**: Virtual consultation queue management

---

**SwiftQueue Hospital** - Revolutionizing healthcare through intelligent queue management. 🏥✨
# Healthcare Queue Management System

A comprehensive healthcare management system built with React (TypeScript) frontend and FastAPI backend, featuring queue management, appointment scheduling, patient check-in, notifications, and hospital navigation.

## Features

### Core Functionality
- **Queue Management**: Real-time queue system with priority levels and AI-powered wait time predictions
- **User Authentication**: Secure login/registration with role-based access (Admin, Staff, Patient)
- **Analytics Dashboard**: Comprehensive analytics with efficiency metrics and performance tracking

### Appointment System
- **Appointment Booking**: Schedule appointments with available services and staff
- **Appointment Management**: View, update, and cancel appointments with status tracking
- **Patient Check-in**: Digital check-in system for appointments with real-time status updates

### Communication & Navigation
- **Notification Center**: In-app notifications with read/unread status and priority levels
- **Hospital Navigation**: Indoor navigation with accessibility features and emergency assistance
- **Real-time Updates**: WebSocket integration for live queue updates and notifications

### Administrative Features
- **Staff Management**: Manage staff schedules and assignments
- **Service Configuration**: Configure medical services and departments
- **Analytics & Reporting**: Detailed performance metrics and patient satisfaction tracking

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Radix UI components
- React Router for navigation
- Axios for API communication
- Supabase for database (optional)

### Backend
- FastAPI (Python)
- SQLAlchemy ORM
- SQLite database (easily configurable for PostgreSQL/MySQL)
- JWT authentication
- WebSocket support
- CORS enabled

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd healthcare-queue-system
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python run.py
   ```

3. **Frontend Setup**
   ```bash
   npm install
   npm run dev
   ```

4. **Database Initialization**
   The database tables will be created automatically when the backend starts.

### Usage

1. **Access the application** at `http://localhost:5173`
2. **Create an admin account** or use the default admin credentials
3. **Configure services and staff** through the admin panel
4. **Patients can join queues** or book appointments
5. **Staff can manage queues** and view analytics

## API Documentation

The API is automatically documented at `http://localhost:8000/docs` when the backend is running.

### Key Endpoints
- `/api/auth/*` - Authentication
- `/api/queue/*` - Queue management
- `/api/appointments/*` - Appointment system
- `/api/checkin/*` - Patient check-in
- `/api/notifications/*` - Notification system
- `/api/navigation/*` - Hospital navigation
- `/api/analytics/*` - Analytics and reporting

## Development

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Project Structure
```
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API routes
│   │   ├── services/        # Business logic
│   │   └── main.py          # FastAPI app
│   └── requirements.txt
├── src/
│   ├── components/          # React components
│   ├── services/            # API services
│   └── types/               # TypeScript types
└── public/                  # Static assets
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
